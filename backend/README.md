# PixelDraft — Phase 4a: Backend (FastAPI)

Serves the full pipeline over HTTP. Loads the trained detector once and reuses it.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/generate` | multipart image upload → `{elements, tree, code, size}` |
| `GET` | `/api/health` | liveness + whether trained weights are present |

## Setup & run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# point at your trained weights from Phase 1
set PIXELDRAFT_WEIGHTS=..\model\runs\detect\ui_detector\weights\best.pt   # Windows
# export PIXELDRAFT_WEIGHTS=../model/.../best.pt                          # Mac/Linux

uvicorn main:app --host 0.0.0.0 --port 8000
```

Interactive docs at http://localhost:8000/docs. Requires the tesseract binary on
PATH (see the Phase-2 README).

## Notes

- Without weights, `/api/generate` returns a clean **503** telling you to train first.
- `service.py` owns the orchestration (detect → hierarchy → extract → codegen) so
  `main.py` stays a thin HTTP layer.
- CORS is open to `http://localhost:3000` for the Next.js dev server.
