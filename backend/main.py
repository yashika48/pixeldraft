"""
main.py — FastAPI app for PixelDraft.   (Phase 4)

Endpoints:
  POST /api/generate   multipart image -> {elements, tree, code, size}
  GET  /api/health     liveness + whether the model weights are present

Env:
  PIXELDRAFT_WEIGHTS   path to trained best.pt (default: ../model/best.pt)
"""

import os
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import service

WEIGHTS = os.environ.get(
    "PIXELDRAFT_WEIGHTS",
    str(Path(__file__).resolve().parent.parent / "model" / "best.pt"),
)

app = FastAPI(title="PixelDraft API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True, "weights_present": Path(WEIGHTS).exists(), "weights": WEIGHTS}


@app.post("/api/generate")
async def generate(file: UploadFile = File(...)):
    if not Path(WEIGHTS).exists():
        raise HTTPException(503, f"Model weights not found at {WEIGHTS}. Train Phase 1 first.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image.")
    data = await file.read()
    try:
        return service.generate(data, WEIGHTS)
    except Exception as e:
        raise HTTPException(500, f"Generation failed: {e}")
