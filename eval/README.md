# PixelDraft — Phase 3: Evaluation Harness

The part most projects skip and the part that most impresses. It answers "how good
is it?" with numbers, not vibes — and exposes the sim-to-real gap honestly.

## Three measurements

| Command | Measures | What it tells you |
|---|---|---|
| `evaluate.py detect` | mAP50, mAP50-95, per-class AP | Detector quality. Run on synthetic val **and** the real test set. |
| `evaluate.py visual` | SSIM between input and rendered output | Does the generated UI *look* like the screenshot? |
| `evaluate.py struct` | precision / recall / F1 on element types | Did it find the right elements (independent of exact boxes)? |

## Setup

```bash
pip install ultralytics scikit-image pillow numpy
```

## Build the real-screenshot test set (the most important step)

Synthetic mAP is easy and not the number that matters. Collect **50–100 real
screenshots** of simple UIs (login forms, dashboards, settings pages, cards) and
hand-label them in YOLO format. Use a free tool like **Label Studio** or
**Roboflow**; export to the same 18 classes (order = `CLASSES` in any module).

Put them in `real_test_set/` mirroring the dataset layout:

```
real_test_set/
  images/val/*.png
  labels/val/*.txt
  data.yaml          ← same classes, val points at images/val
```

## Run the evaluation

```bash
cd eval

# detection on synthetic val
python evaluate.py detect --weights ../model/best.pt --data ../data_gen/dataset/data.yaml

# detection on the REAL test set  ← the honest number
python evaluate.py detect --weights ../model/best.pt --data real_test_set/data.yaml

# visual similarity for one example
#   1) generate React for input.png  2) render+screenshot it as out.png (see frontend live preview)
python evaluate.py visual --orig input.png --rendered out.png

# structural: did we find the right element types?
python evaluate.py struct --weights ../model/best.pt --img s.png --label s.txt
```

## The story this tells (use it in interviews)

- "Synthetic val mAP50 = X, real test mAP50 = Y. The Y−X gap is the sim-to-real
  cost; I narrowed it by widening the generator's domain randomization."
- "SSIM on rendered output averages Z — layout transfers well; exact styling less so."
- "Weakest classes are radio/toggle (small elements); the fix is upstream in data
  generation, not model size." ← data-centric thinking, the senior signal.

## Build a failure gallery

Save the 8–10 worst cases (low SSIM or wrong structure) with one sentence each on
*why* it failed. Owning your failure modes is the single most credible thing in the
whole project — put a few in your README/demo.
