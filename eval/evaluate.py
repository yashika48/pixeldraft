"""
evaluate.py — How good is PixelDraft, honestly?   (Phase 3)

Three layers, because "it looks right" is not a metric:

  1. DETECTION  — mAP / per-class AP (delegates to YOLO). Run on synthetic val
                  AND the real test set; the gap is your sim-to-real story.
  2. VISUAL     — render generated React, screenshot it, SSIM vs the input.
  3. STRUCTURAL — predicted element-type multiset vs ground truth (precision/recall/F1).

Usage:
    python evaluate.py detect --weights best.pt --data ../data_gen/dataset/data.yaml
    python evaluate.py visual --orig input.png --rendered out.png
    python evaluate.py struct --weights best.pt --img s.png --label s.txt
"""

import argparse
from collections import Counter

CLASSES = ["button", "input", "textarea", "checkbox", "radio", "toggle", "select",
           "label", "heading", "paragraph", "link", "badge", "avatar",
           "icon_button", "image", "card", "navbar", "list_item"]


def detect_metrics(weights, data):
    from ultralytics import YOLO
    m = YOLO(weights).val(data=data)
    print("\n=== DETECTION ===")
    print(f"mAP50:    {m.box.map50:.3f}")
    print(f"mAP50-95: {m.box.map:.3f}")
    try:
        for i, ap in enumerate(m.box.maps):
            name = CLASSES[i] if i < len(CLASSES) else str(i)
            print(f"  {name:12s} AP: {ap:.3f}")
    except Exception:
        pass
    print("\nRun on BOTH synthetic val and the real test set; report the gap.")


def visual_similarity(orig_path, rendered_path):
    import numpy as np
    from PIL import Image
    from skimage.metrics import structural_similarity as ssim
    a = Image.open(orig_path).convert("L")
    b = Image.open(rendered_path).convert("L")
    size = (min(a.size[0], b.size[0]), min(a.size[1], b.size[1]))
    a = np.asarray(a.resize(size)); b = np.asarray(b.resize(size))
    score = ssim(a, b)
    print("\n=== VISUAL (SSIM) ===")
    print(f"SSIM: {score:.3f}   (1.0 identical; 0.6+ = good layout match)")
    return score


def _detect_types(weights, img):
    from ultralytics import YOLO
    r = YOLO(weights)(img, conf=0.25, verbose=False)[0]
    return [r.names[int(b.cls)] for b in r.boxes]


def structural(weights, img, label):
    pred = Counter(_detect_types(weights, img))
    truth = Counter(CLASSES[int(l.split()[0])] for l in open(label))
    tp = sum((pred & truth).values())
    prec = tp / sum(pred.values()) if pred else 0
    rec = tp / sum(truth.values()) if truth else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    print("\n=== STRUCTURAL (element-type multiset) ===")
    print(f"precision: {prec:.3f}  recall: {rec:.3f}  f1: {f1:.3f}")
    print(f"predicted {sum(pred.values())} elements, truth {sum(truth.values())}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect"); d.add_argument("--weights", required=True); d.add_argument("--data", required=True)
    v = sub.add_parser("visual"); v.add_argument("--orig", required=True); v.add_argument("--rendered", required=True)
    s = sub.add_parser("struct"); s.add_argument("--weights", required=True); s.add_argument("--img", required=True); s.add_argument("--label", required=True)
    args = ap.parse_args()
    {"detect": lambda: detect_metrics(args.weights, args.data),
     "visual": lambda: visual_similarity(args.orig, args.rendered),
     "struct": lambda: structural(args.weights, args.img, args.label)}[args.cmd]()


if __name__ == "__main__":
    main()
