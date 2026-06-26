# PixelDraft — Phase 0: Synthetic Data Generator

This phase produces the labeled dataset you'll train the detector on in Phase 1.
It generates random UIs, renders them, and writes perfect YOLO labels — **no
manual annotation**.

## What's here

| File | Role |
|---|---|
| `grammar.py` | Generates random-but-valid UIs as HTML. Every element is tagged `data-ui="<type>"`. Domain randomization (palette, fonts, spacing, light/dark) is baked in. |
| `render.py` | Headless Chromium renders each UI, screenshots it, reads every element's box via `getBoundingClientRect`, and writes YOLO-format labels. |
| `visualize.py` | Draws the labels back onto an image so you can confirm they align. Always eyeball a few before training. |

The 18 element classes live in `grammar.py` (`CLASSES`) — the list order defines
the YOLO class ids, so don't reorder it once you've generated data.

## Setup (Windows)

```bash
cd data_gen
python -m venv .venv
.venv\Scripts\activate
pip install playwright pillow
python -m playwright install chromium
```

(On Mac/Linux the only change is `source .venv/bin/activate`.)

## Generate the dataset

```bash
# quick smoke test first — 20 samples, then look at one
python render.py --n 20 --out dataset
python visualize.py --img dataset/images/train/000000.png
#  open overlay_check.png — every box should sit tightly on its element

# once it looks right, generate the real thing
python render.py --n 4000 --val-split 0.1 --out dataset
```

On a normal laptop this renders roughly 5–15 samples/sec, so a few thousand
takes minutes, not hours. Start with ~3–5k; you can always generate more.

## Output (ready for Ultralytics YOLO)

```
dataset/
  images/train/*.png   labels/train/*.txt
  images/val/*.png     labels/val/*.txt
  data.yaml            ← points YOLO at the splits + class names
```

Each label line is: `class_id  x_center  y_center  width  height` (normalized 0–1).

## When this phase is "done"

- A few thousand samples generated.
- `visualize.py` shows boxes landing tightly on the right elements across several
  random samples (light *and* dark, different layouts).
- `data.yaml` lists all 18 classes.

Then move to Phase 1: `yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=50 imgsz=960`

## Tuning knobs (worth knowing for your interview defense)

- **More variety** → edit the palettes, fonts, and block choices in `grammar.py`.
  Wider synthetic distribution = better transfer to real screenshots (this is your
  sim-to-real lever).
- **New component** → add a builder method + its name to `CLASSES`. It flows
  through labeling automatically.
- **Class balance** → if a class is rare (e.g. `radio`), bias the generator to
  include it more often so the detector sees enough examples.
