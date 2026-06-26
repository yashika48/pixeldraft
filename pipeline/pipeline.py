"""
pipeline.py — The full screenshot -> React pipeline.   (Phase 2 glue)

    elements (from detector)  ->  hierarchy  ->  extract  ->  codegen  ->  JSX

Two entry points:
  run(elements, image_path)        : from detector output
  run_from_labels(label, image)    : from Phase-0 YOLO ground truth (for testing
                                     the pipeline without a trained model)
"""

from PIL import Image
from hierarchy import build_tree
from extract import enrich
from codegen import generate_react

# class id -> name, must match grammar.CLASSES order
CLASSES = ["button", "input", "textarea", "checkbox", "radio", "toggle", "select",
           "label", "heading", "paragraph", "link", "badge", "avatar",
           "icon_button", "image", "card", "navbar", "list_item"]


def run(elements, image_path, component_name="GeneratedUI"):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    tree = build_tree(elements, w, h)
    enrich(tree, img)
    code = generate_react(tree, component_name)
    return {"tree": tree, "code": code, "size": [w, h]}


def run_from_labels(label_path, image_path, **kw):
    """Read a YOLO .txt label, convert to pixel boxes, run the pipeline."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    elements = []
    for line in open(label_path):
        cid, xc, yc, bw, bh = line.split()
        cid = int(cid); xc, yc, bw, bh = map(float, (xc, yc, bw, bh))
        x1 = (xc - bw / 2) * w; y1 = (yc - bh / 2) * h
        x2 = (xc + bw / 2) * w; y2 = (yc + bh / 2) * h
        elements.append({"type": CLASSES[cid], "box": [x1, y1, x2, y2], "conf": 1.0})
    return run(elements, image_path, **kw)


if __name__ == "__main__":
    import sys
    out = run_from_labels(sys.argv[1], sys.argv[2])
    print(out["code"])
