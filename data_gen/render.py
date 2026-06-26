"""
render.py — Render generated UIs and emit (screenshot, labels) pairs.

This is the labeling machine. For each UI:
  1. Load the HTML in a headless Chromium page.
  2. Screenshot it.
  3. Ask the browser for the bounding box of every [data-ui] element via
     getBoundingClientRect() — perfect ground truth, zero manual annotation.
  4. Write a YOLO-format label file (one line per element):
        <class_id> <x_center> <y_center> <width> <height>   (all normalized 0..1)

Output layout (YOLO/Ultralytics standard, ready for training):
    dataset/
      images/train/000123.png
      labels/train/000123.txt
      images/val/...
      labels/val/...
      data.yaml

Run:
    python render.py --n 3000 --val-split 0.1
"""

import argparse
import os
import random
from pathlib import Path

from playwright.sync_api import sync_playwright

from grammar import generate_html, CLASSES, CLASS_TO_ID

# Viewport is randomized per-sample within these bounds (domain randomization).
VIEWPORTS = [(1280, 800), (1024, 768), (1440, 900), (1100, 850), (960, 720)]

# JS run inside the page: collect every labeled element's box + type.
# We use getBoundingClientRect (viewport coords) and add scroll offset so boxes
# match a full-page screenshot.
COLLECT_JS = """
() => {
  const out = [];
  const sx = window.scrollX, sy = window.scrollY;
  document.querySelectorAll('[data-ui]').forEach(el => {
    const r = el.getBoundingClientRect();
    // skip zero-size / off-screen elements
    if (r.width < 4 || r.height < 4) return;
    out.push({
      type: el.getAttribute('data-ui'),
      x: r.x + sx, y: r.y + sy, w: r.width, h: r.height
    });
  });
  return {
    boxes: out,
    pageW: document.documentElement.scrollWidth,
    pageH: document.documentElement.scrollHeight
  };
}
"""


def to_yolo_line(box, page_w, page_h):
    """Convert one {type,x,y,w,h} box (pixels) to a normalized YOLO line."""
    cid = CLASS_TO_ID[box["type"]]
    xc = (box["x"] + box["w"] / 2) / page_w
    yc = (box["y"] + box["h"] / 2) / page_h
    w = box["w"] / page_w
    h = box["h"] / page_h
    # clamp to [0,1] for safety
    clamp = lambda v: max(0.0, min(1.0, v))
    return f"{cid} {clamp(xc):.6f} {clamp(yc):.6f} {clamp(w):.6f} {clamp(h):.6f}"


def write_data_yaml(root: Path):
    names = "\n".join(f"  {i}: {c}" for i, c in enumerate(CLASSES))
    (root / "data.yaml").write_text(
        f"path: {root.resolve()}\n"
        f"train: images/train\n"
        f"val: images/val\n\n"
        f"nc: {len(CLASSES)}\n"
        f"names:\n{names}\n",
        encoding="utf-8",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000, help="total samples to generate")
    ap.add_argument("--val-split", type=float, default=0.1, help="fraction for validation")
    ap.add_argument("--out", default="dataset", help="output root dir")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    random.seed(args.seed)
    root = Path(args.out)
    for split in ("train", "val"):
        (root / "images" / split).mkdir(parents=True, exist_ok=True)
        (root / "labels" / split).mkdir(parents=True, exist_ok=True)
    write_data_yaml(root)

    n_val = int(args.n * args.val_split)
    val_ids = set(random.sample(range(args.n), n_val))

    kept = skipped = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for i in range(args.n):
            vw, vh = random.choice(VIEWPORTS)
            page.set_viewport_size({"width": vw, "height": vh})
            page.set_content(generate_html(), wait_until="networkidle")

            data = page.evaluate(COLLECT_JS)
            boxes, page_w, page_h = data["boxes"], data["pageW"], data["pageH"]
            if not boxes:
                skipped += 1
                continue

            split = "val" if i in val_ids else "train"
            stem = f"{i:06d}"
            img_path = root / "images" / split / f"{stem}.png"
            lbl_path = root / "labels" / split / f"{stem}.txt"

            page.screenshot(path=str(img_path), full_page=True)
            lines = [to_yolo_line(b, page_w, page_h) for b in boxes]
            lbl_path.write_text("\n".join(lines), encoding="utf-8")
            kept += 1

            if kept % 200 == 0:
                print(f"  {kept} written ({split})...")

        browser.close()

    print(f"\nDone. {kept} samples written, {skipped} skipped (empty).")
    print(f"Dataset at: {root.resolve()}")
    print(f"Train on it with:  yolo detect train data={root/'data.yaml'} model=yolov8n.pt epochs=50 imgsz=960")


if __name__ == "__main__":
    main()
