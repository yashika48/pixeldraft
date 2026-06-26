# PixelDraft — Phase 2: Boxes → React

Turns the detector's flat list of boxes into clean, nested **React + Tailwind**.
This is the deterministic, inspectable core of PixelDraft — no second model.

## Flow

```
elements [{type, box, conf}]
        │  hierarchy.py   → containment tree + flex direction / gap / padding
        ▼
      tree
        │  extract.py     → OCR text + sampled colors (snapped to Tailwind tokens)
        ▼
   enriched tree
        │  codegen.py     → JSX string (one component)
        ▼
   React + Tailwind
```

| File | Role |
|---|---|
| `hierarchy.py` | Boxes → containment tree. Infers row/col, gap, padding, justify geometrically. |
| `extract.py` | OCR (pytesseract) for text; pixel sampling for colors, snapped to Tailwind tokens. |
| `codegen.py` | Tree → React + Tailwind. One template per element type; pixels snapped to the Tailwind spacing scale. |
| `pipeline.py` | Glue: `run(elements, image)` for detector output, `run_from_labels(label, image)` to test on Phase-0 ground truth. |

## Setup

```bash
pip install pillow pytesseract
# Windows: install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
#          then ensure tesseract.exe is on PATH
# Mac:     brew install tesseract     Linux: apt-get install tesseract-ocr
```

## Try it (no trained model needed)

You can run the whole pipeline on a Phase-0 sample using its ground-truth labels —
a great way to verify hierarchy + codegen independently of the detector:

```bash
cd pipeline
python pipeline.py ../data_gen/dataset/labels/train/000000.txt \
                   ../data_gen/dataset/images/train/000000.png
```

With a trained model, feed `infer.py`'s output into `run(elements, image_path)` instead.

## Honest limitations (state these; don't hide them)

- **OCR is imperfect** on small/styled text — structure is reliable, exact strings less so.
  This is a known, measurable weakness, not a bug.
- **Hierarchy is geometric**, so heavily overlapping or absolutely-positioned layouts can
  nest wrong. Fine for the clean UIs in v1 scope.
- **Colors are sampled + snapped**, so gradients/images approximate to a flat token.

These are exactly the things the Phase-3 eval harness measures.

## Design decisions worth defending

- **Deterministic codegen, not a learned decoder** — explainable, debuggable, reliable for v1.
  A learned decoder is the documented next step, not a v1 requirement.
- **Snap everything to Tailwind tokens** — output reads like human-written code, not a 400-line
  inline-style dump.
- **Emit flex/grid, never absolute positioning** — the output reflows, which is what makes the
  "responsive" claim real (inferred, not pixel-perfect — say so).
