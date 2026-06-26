"""Run the trained detector on a real screenshot, then generate React."""
import sys, argparse
from pathlib import Path
from PIL import Image
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hierarchy import build_tree
from extract import enrich
from codegen import generate_react

ap = argparse.ArgumentParser()
ap.add_argument("--weights", required=True)
ap.add_argument("--img", required=True)
ap.add_argument("--out", default="generated.jsx")
ap.add_argument("--conf", type=float, default=0.35)
args = ap.parse_args()

img = Image.open(args.img).convert("RGB")
w, h = img.size

# 1. detect with the trained model
result = YOLO(args.weights)(args.img, conf=args.conf, verbose=False)[0]
names = result.names
elements = []
for b in result.boxes:
    x1, y1, x2, y2 = b.xyxy[0].tolist()
    elements.append({"type": names[int(b.cls)],
                     "box": [x1, y1, x2, y2], "conf": float(b.conf)})
print(f"{len(elements)} elements detected")

# 2. hierarchy -> 3. extract text/color -> 4. codegen
tree = build_tree(elements, w, h)
enrich(tree, img)
code = generate_react(tree)

Path(args.out).write_text(code, encoding="utf-8")
print(f"React written to {args.out}")