"""
service.py — Orchestrates detection -> pipeline for the API. (Phase 4)

Keeps the FastAPI layer thin: this module owns "image bytes in, result out".
Loads the YOLO model once at import and reuses it.
"""

import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

# make the pipeline package importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from hierarchy import build_tree
from extract import enrich
from codegen import generate_react

CLASSES = ["button", "input", "textarea", "checkbox", "radio", "toggle", "select",
           "label", "heading", "paragraph", "link", "badge", "avatar",
           "icon_button", "image", "card", "navbar", "list_item"]

_MODEL = None


def _load_model(weights):
    global _MODEL
    if _MODEL is None:
        from ultralytics import YOLO
        _MODEL = YOLO(weights)
    return _MODEL


def detect(img: Image.Image, weights: str, conf=0.25):
    """Return list of {type, box, conf} for a PIL image."""
    model = _load_model(weights)
    result = model(img, conf=conf, verbose=False)[0]
    names = result.names
    els = []
    for b in result.boxes:
        x1, y1, x2, y2 = b.xyxy[0].tolist()
        els.append({"type": names[int(b.cls)],
                    "box": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "conf": round(float(b.conf), 3)})
    return els


def generate(image_bytes: bytes, weights: str):
    """Full path: bytes -> {elements, tree, code, size}."""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    elements = detect(img, weights)
    w, h = img.size
    tree = build_tree(elements, w, h)
    enrich(tree, img)
    code = generate_react(tree)
    return {"elements": elements, "tree": tree, "code": code, "size": [w, h]}
