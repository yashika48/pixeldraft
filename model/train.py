"""
train.py — Train the UI-element detector (Phase 1).

Thin, well-documented wrapper around Ultralytics YOLO so the choices are explicit
and defensible in an interview. Nothing magic here — but you should understand
every flag.

Usage:
    python train.py --data ../data_gen/dataset/data.yaml --epochs 60
    python train.py --data ../data_gen/dataset/data.yaml --model yolov8s.pt   # bigger/stronger

After training, weights land in  runs/detect/<name>/weights/best.pt
"""

import argparse
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to data.yaml from Phase 0")
    ap.add_argument("--model", default="yolov8n.pt",
                    help="pretrained checkpoint. n=nano (fast), s=small, m=medium (stronger, slower)")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--imgsz", type=int, default=960,
                    help="UIs have small elements (checkboxes); keep this high. 960 is a good default.")
    ap.add_argument("--batch", type=int, default=8, help="lower if you hit out-of-memory")
    ap.add_argument("--name", default="ui_detector")
    args = ap.parse_args()

    # Start from COCO-pretrained weights: transfer learning converges far faster
    # than training from scratch (which is why the smoke test showed zeros).
    model = YOLO(args.model)

    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        patience=15,          # early-stop if val stops improving for 15 epochs
        # --- augmentation: keep it UI-appropriate ---
        # UIs are axis-aligned and have a fixed orientation, so DON'T flip/rotate.
        workers=0, 
        fliplr=0.0,           # no horizontal flip (a left nav is not a right nav)
        flipud=0.0,           # no vertical flip
        degrees=0.0,          # no rotation
        mosaic=0.0,           # mosaic mixes 4 images — wrong for whole-page layouts
        hsv_h=0.015, hsv_s=0.4, hsv_v=0.4,  # mild color jitter is fine and helps
        translate=0.05, scale=0.2,           # small position/scale jitter is realistic
    )

    # Quick validation summary on the val split
    metrics = model.val()
    print("\n=== Validation summary ===")
    print(f"mAP50:    {metrics.box.map50:.3f}")
    print(f"mAP50-95: {metrics.box.map:.3f}")
    print("Per-class AP50 is in the val output above and saved under runs/.")
    print(f"\nBest weights: runs/detect/{args.name}/weights/best.pt")


if __name__ == "__main__":
    main()
