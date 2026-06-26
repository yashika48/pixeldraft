# PixelDraft — Phase 1: Train the UI Detector

Train an object detector to find UI elements in a screenshot, using the synthetic
dataset from Phase 0. Output is `best.pt` — the trained model the rest of the
pipeline depends on.

## What's here

| File | Role |
|---|---|
| `train.py` | Trains YOLOv8 on your dataset with UI-appropriate settings. Run on your machine if you have an NVIDIA GPU. |
| `train_colab.ipynb` | Same training on Google Colab's **free GPU**. Use this if your machine is CPU-only. |
| `infer.py` | Loads `best.pt` and detects elements in one image. Outputs the clean element list Phase 2 consumes. |

## Which path to use

- **NVIDIA GPU on your machine** → use `train.py` locally.
- **CPU only / no GPU** → use `train_colab.ipynb` (free T4 GPU). Training on CPU is
  painfully slow; don't.

## Local training (if you have a GPU)

```bash
cd model
pip install ultralytics
python train.py --data ../data_gen/dataset/data.yaml --epochs 60
```

Weights land in `runs/detect/ui_detector/weights/best.pt`.

## Colab training (free GPU)

1. Zip your Phase-0 `dataset/` folder.
2. Open `train_colab.ipynb` in [Colab](https://colab.research.google.com/) → Runtime → T4 GPU.
3. Run the cells (upload the zip when prompted).
4. Download `best.pt` at the end and put it next to `infer.py`.

## Test the trained model

```bash
python infer.py --weights best.pt --img some_screenshot.png --save annotated.png
```

You get a JSON list of `{type, box, conf}` and an annotated image. **Always eyeball
the annotated image on a few real screenshots** — this is your first honest look at
the sim-to-real gap.

## Key training choices (be ready to defend these)

- **Start from pretrained weights** (`yolov8n.pt`), not scratch. Transfer learning
  converges far faster — the smoke test showed zeros precisely because it skipped this.
- **`imgsz=960`, not the default 640.** UI elements (checkboxes, radios) are tiny;
  downscaling too aggressively loses them. This directly helps small-class AP.
- **No flips / rotation / mosaic augmentation.** UIs are orientation-fixed and
  whole-page — a horizontally flipped layout isn't a real UI, and mosaic (stitching
  4 images) destroys page structure. Mild color/scale jitter is kept because it's realistic.
- **`yolov8n` baseline, `yolov8s`/`m` as the upgrade.** Start small for fast iteration;
  scale up if a class is stubbornly weak.

## What "good" looks like

On clean synthetic val data, expect **high mAP50** (0.8+) fairly quickly — the data is
consistent. The number that matters for your resume is the one on the **real-screenshot
test set** you build in Phase 3; that gap (synthetic mAP minus real mAP) is the honest
story. If a specific class lags (radios and toggles often do), bias the Phase-0 generator
to produce more of them and retrain.

## When this phase is "done"

- `best.pt` exists and `infer.py` runs on it.
- mAP50 on synthetic val is solidly high.
- Annotated predictions on a few real screenshots look reasonable (imperfect is fine —
  that's the gap you'll measure and report, not hide).

Then move to **Phase 2**: detected boxes → containment tree → React + Tailwind.
