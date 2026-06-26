"""
infer.py — Run the trained detector on a single image (Phase 1 output).

Returns a clean list of detected elements: type, box (pixels), confidence.
This is the exact structure Phase 2 (hierarchy reconstruction) consumes, so it's
the seam between the model and the rest of the pipeline.

Usage:
    python infer.py --weights runs/detect/ui_detector/weights/best.pt --img test.png
    python infer.py --weights best.pt --img test.png --save annotated.png
"""

import argparse
import json
from ultralytics import YOLO


def detect(weights, img_path, conf=0.25):
    """Run detection; return list of {type, box:[x1,y1,x2,y2], conf}."""
    model = YOLO(weights)
    result = model(img_path, conf=conf, verbose=False)[0]
    names = result.names  # class_id -> name

    elements = []
    for b in result.boxes:
        x1, y1, x2, y2 = b.xyxy[0].tolist()
        elements.append({
            "type": names[int(b.cls)],
            "box": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
            "conf": round(float(b.conf), 3),
        })
    # sort top-to-bottom, then left-to-right (stable, predictable order)
    elements.sort(key=lambda e: (e["box"][1], e["box"][0]))
    return elements, result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--img", required=True)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--save", default=None, help="optional path to save annotated image")
    args = ap.parse_args()

    elements, result = detect(args.weights, args.img, args.conf)
    print(json.dumps(elements, indent=2))
    print(f"\n{len(elements)} elements detected.")

    if args.save:
        result.save(filename=args.save)
        print(f"Annotated image saved to {args.save}")


if __name__ == "__main__":
    main()
