<div align="center">

# PixelDraft

### Screenshot to editable React, powered by a UI-element detector I trained from scratch

Upload a screenshot of an interface. A **custom-trained object-detection model** locates every
UI element, a **deterministic algorithm** reconstructs the layout hierarchy, and a **code generator**
emits clean, editable **React + Tailwind** — all running locally.

**No vision-language model. No API. The ML is trained, not called.**

</div>

---

## Why this project exists

The common "screenshot to code" tool is a single call to a vision-language model — it trains nothing.
PixelDraft is the opposite: I built and trained the model that does the hard part, on a **synthetic
dataset I generated myself**, and evaluated it honestly on real screenshots. That makes this a
computer-vision engineering project with a real ML core, not an API wrapper.

```
screenshot --> [TRAINED YOLO detector] --> UI element boxes + classes
                                             |
                                             v
                                 [containment algorithm] --> layout tree
                                             |
                             OCR (text) + pixel sampling (color)
                                             v
                                 [deterministic codegen] --> React + Tailwind
```

## What I built

- **A custom UI-element detector** — YOLOv8 trained to recognize 18 UI component types
  (buttons, inputs, cards, navbars, list items, avatars, etc.).
- **A synthetic data pipeline** — a generator that programmatically builds labeled UIs and renders
  them with a headless browser, producing thousands of training images with **perfect labels and zero
  manual annotation**.
- **A deterministic screenshot-to-React pipeline** — containment-based hierarchy reconstruction, OCR for
  text, pixel sampling for colors, snapped to Tailwind tokens.
- **A full-stack product** — a FastAPI backend serving the pipeline and a Next.js frontend with
  drag-and-drop upload, a live detection overlay, and generated code with copy-to-clipboard.
- **An honest evaluation** — detection metrics, rendered visual-similarity (SSIM), and a real-screenshot
  test gallery measuring the sim-to-real gap.

## The engineering story (and an honest iteration)

The most interesting part of this project is a real ML-engineering loop I worked through:

1. **v1** trained on simple synthetic UIs. It performed near-perfectly on synthetic data but **degraded
   on dense, real-world layouts** (e.g. dashboards with sidebars) — it flattened structure it had never
   seen in training.
2. I **diagnosed** this as a gap in the training distribution, not a model-size problem.
3. I **expanded the synthetic generator** to produce dense, sidebar-based "app-shell" layouts, then
   **regenerated the dataset and retrained**.
4. **v2** measurably improved structural coverage on dense screenshots (detecting sidebar/nav regions
   and more content), confirming the data-centric fix.

This data-centric debugging loop — diagnose a failure mode, trace it to the data, fix the generator,
retrain, measure — is the core of the project.

## Honest limitations (by design)

- **Output is a structural starting point, not a pixel-perfect clone.** No tool in this space achieves
  pixel-perfection; PixelDraft produces editable scaffolding.
- **Best on clean, simple UIs** (login forms, cards, settings). Dense real-world dashboards are handled
  but with noisier detection — improved in v2, still imperfect.
- **OCR and color are approximate** on small, anti-aliased real text — structure is reliable, exact text
  less so.
- **Sim-to-real gap:** trained on synthetic UIs; real screenshots score lower. This is measured, not hidden.

## Tech stack

**ML / pipeline:** Python, Ultralytics YOLOv8, PyTorch (CUDA), Playwright (synthetic rendering),
Tesseract OCR, Pillow, scikit-image (SSIM)
**Backend:** FastAPI, Uvicorn
**Frontend:** Next.js, React

## Architecture

```
pixeldraft/
  data_gen/     synthetic UI generator + renderer + label visualizer
  model/        training, inference, trained weights
  pipeline/     hierarchy reconstruction, OCR/color extraction, React codegen
  eval/         detection / visual / structural metrics + real-screenshot gallery
  backend/      FastAPI service (/api/generate)
  frontend/     Next.js product (upload, detection overlay, generated code)
```

## Running it locally

Requires Python 3.11+, Node 18+, Tesseract OCR, and (for training) an NVIDIA GPU or Google Colab.

```bash
# generate data + train (or use the provided Colab notebook)
cd data_gen && python render.py --n 4000 --val-split 0.1 --out dataset
cd ../model && python train.py --data ../data_gen/dataset/data.yaml --epochs 25 --batch 4 --imgsz 640

# run the product (two terminals)
cd backend  && uvicorn main:app --port 8000      # set PIXELDRAFT_WEIGHTS to your best.pt
cd frontend && npm install && npm run dev          # http://localhost:3000
```

## Results

See `eval/` for the evaluation gallery and metrics. Demo and before/after (v1 vs v2 on dense layouts)
in the screenshots below.
<img width="1088" height="576" alt="demo " src="https://github.com/user-attachments/assets/f52c0c93-fd3e-4180-9a54-7c9c6e7f7b59" />

<img width="1599" height="759" alt="WhatsApp Image 2026-06-26 at 8 53 39 PM" src="https://github.com/user-attachments/assets/f6036fee-abb2-4db8-9594-1accd9207e10" />
<img width="1600" height="749" alt="WhatsApp Image 2026-06-26 at 8 57 43 PM" src="https://github.com/user-attachments/assets/21eb141b-c7a4-4576-9775-90da2e2a446b" />

<img width="1599" height="748" alt="WhatsApp Image 2026-06-26 at 8 56 37 PM" src="https://github.com/user-attachments/assets/4be8501b-e554-44aa-82d7-d14956998ad2" />




---

<div align="center">
Built end-to-end: synthetic data -> trained detection model -> deterministic codegen -> full-stack product.
</div>
