"""
visualize.py — Sanity-check tool. Draws ground-truth boxes onto a sample so you
can confirm labels align with elements. Run this after generating data.

    python visualize.py --img dataset/images/train/000000.png
"""
import argparse
import random
from pathlib import Path
from PIL import Image, ImageDraw

from grammar import CLASSES

random.seed(7)
COLORS = {c: (random.randint(40, 255), random.randint(40, 255), random.randint(40, 255))
          for c in CLASSES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True, help="path to an image; its label is inferred")
    ap.add_argument("--out", default="overlay_check.png")
    args = ap.parse_args()

    img_path = Path(args.img)
    lbl_path = Path(str(img_path).replace("images", "labels").replace(".png", ".txt"))
    img = Image.open(img_path).convert("RGB")
    W, H = img.size
    d = ImageDraw.Draw(img)

    for line in lbl_path.read_text().splitlines():
        cid, xc, yc, w, h = line.split()
        cid = int(cid); xc, yc, w, h = map(float, (xc, yc, w, h))
        x1, y1 = (xc - w / 2) * W, (yc - h / 2) * H
        x2, y2 = (xc + w / 2) * W, (yc + h / 2) * H
        col = COLORS[CLASSES[cid]]
        d.rectangle([x1, y1, x2, y2], outline=col, width=2)
        d.text((x1 + 2, y1 + 2), CLASSES[cid], fill=col)

    img.save(args.out)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
