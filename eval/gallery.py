"""
gallery.py — Build a real-world evaluation gallery for PixelDraft.

For every screenshot in a folder:
  1. run the trained detector
  2. generate React (full pipeline)
  3. render the React headlessly and compare to the original (SSIM)
  4. record element count + average confidence
Then write an HTML gallery and a markdown report.

Usage (from the eval/ folder):
  python gallery.py --weights ..\\model\\runs\\detect\\ui_detector\\weights\\best.pt --dir ..\\real_samples --out report
"""
import sys, argparse, statistics
from pathlib import Path
from PIL import Image
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from hierarchy import build_tree
from extract import enrich
from codegen import generate_react

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def detect(model, img_path, img, conf):
    r = model(str(img_path), conf=conf, verbose=False)[0]
    names = r.names
    els, confs = [], []
    for b in r.boxes:
        x1, y1, x2, y2 = b.xyxy[0].tolist()
        els.append({"type": names[int(b.cls)], "box": [x1, y1, x2, y2], "conf": float(b.conf)})
        confs.append(float(b.conf))
    annotated = r.plot()  # numpy BGR array with boxes drawn
    return els, confs, annotated


def render_and_ssim(code, original_img, work_dir, stem):
    """Render the generated React headlessly, screenshot it, SSIM vs original."""
    try:
        import numpy as np
        from skimage.metrics import structural_similarity as ssim
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return None
    body = code.replace("export default ", "", 1)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{margin:0;padding:16px;background:#fff}}</style></head>
<body><div id="root"></div>
<script type="text/babel" data-presets="react">
{body}
ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(GeneratedUI));
</script></body></html>"""
    htmlf = work_dir / f"{stem}_render.html"
    htmlf.write_text(html, encoding="utf-8")
    shot = work_dir / f"{stem}_render.png"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": original_img.size[0], "height": original_img.size[1]})
            pg.goto(htmlf.as_uri(), wait_until="networkidle", timeout=15000)
            pg.wait_for_timeout(1500)
            pg.screenshot(path=str(shot), full_page=True)
            b.close()
    except Exception:
        return None
    a = original_img.convert("L")
    bimg = Image.open(shot).convert("L")
    size = (min(a.size[0], bimg.size[0]), min(a.size[1], bimg.size[1]))
    import numpy as np
    aa = np.asarray(a.resize(size)); bb = np.asarray(bimg.resize(size))
    return round(float(ssim(aa, bb)), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", default="report")
    ap.add_argument("--conf", type=float, default=0.35)
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(exist_ok=True)
    assets = out / "assets"; assets.mkdir(exist_ok=True)
    model = YOLO(args.weights)
    rows = []

    imgs = [p for p in Path(args.dir).iterdir() if p.suffix.lower() in IMG_EXT]
    print(f"Found {len(imgs)} screenshots")
    for img_path in imgs:
        stem = img_path.stem
        print(f"  processing {img_path.name} ...")
        img = Image.open(img_path).convert("RGB")
        els, confs, annotated = detect(model, img_path, img, args.conf)

        tree = build_tree(els, *img.size)
        enrich(tree, img)
        code = generate_react(tree)

        # save assets
        Image.fromarray(annotated[:, :, ::-1]).save(assets / f"{stem}_det.png")  # BGR->RGB
        (assets / f"{stem}.jsx").write_text(code, encoding="utf-8")

        ssim_score = render_and_ssim(code, img, assets, stem)
        rows.append({
            "name": img_path.name, "stem": stem,
            "n": len(els),
            "avg_conf": round(statistics.mean(confs), 3) if confs else 0.0,
            "ssim": ssim_score,
        })

    # ---- markdown report ----
    md = ["# PixelDraft — Real-World Evaluation\n",
          "End-to-end results on real screenshots the model never saw during training.\n",
          "| Screenshot | Elements | Avg confidence | Visual SSIM |",
          "|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['name']} | {r['n']} | {r['avg_conf']} | {r['ssim'] if r['ssim'] is not None else 'n/a'} |")
    avg_ssim = [r["ssim"] for r in rows if r["ssim"] is not None]
    if avg_ssim:
        md.append(f"\n**Average visual SSIM across {len(avg_ssim)} samples: {round(sum(avg_ssim)/len(avg_ssim),3)}**")
    md.append("\n## Honest notes\n- Trained on synthetic UIs; these are real screenshots, so this is the sim-to-real result.\n"
              "- Output is a structural starting point, not a pixel-perfect clone.\n"
              "- OCR and layout degrade on dense/complex real UIs (see failure cases below).\n")
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")

    # ---- HTML gallery ----
    cards = []
    for r in rows:
        cards.append(f"""
      <div class="card">
        <h3>{r['name']}</h3>
        <div class="metrics">elements: <b>{r['n']}</b> &nbsp; avg conf: <b>{r['avg_conf']}</b> &nbsp; SSIM: <b>{r['ssim'] if r['ssim'] is not None else 'n/a'}</b></div>
        <div class="imgs">
          <figure><figcaption>detected</figcaption><img src="assets/{r['stem']}_det.png"></figure>
          <figure><figcaption>generated render</figcaption><img src="assets/{r['stem']}_render.png" onerror="this.style.opacity=0.2"></figure>
        </div>
      </div>""")
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>PixelDraft Evaluation</title>
<style>
body{{font-family:system-ui,sans-serif;background:#0e1726;color:#e8eef7;margin:0;padding:32px}}
h1{{font-family:monospace}} .card{{background:#131d30;border:1px solid #24324d;border-radius:12px;padding:20px;margin:20px 0}}
.metrics{{font-family:monospace;color:#5cc8ff;margin:8px 0 16px}} .imgs{{display:flex;gap:16px;flex-wrap:wrap}}
figure{{margin:0;flex:1;min-width:320px}} figcaption{{font-family:monospace;font-size:12px;color:#8094b3;margin-bottom:6px}}
img{{width:100%;border:1px solid #24324d;border-radius:8px;background:#fff}}
</style></head><body>
<h1>PixelDraft — Real-World Evaluation</h1>
<p>End-to-end results on real screenshots the model never saw in training.</p>
{''.join(cards)}
</body></html>"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"\nDone. Open {out/'index.html'} in a browser, and {out/'report.md'} for the README.")


if __name__ == "__main__":
    main()