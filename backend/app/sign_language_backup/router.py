from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.sign_language.adapter import SignLanguageAdapter

router = APIRouter(prefix="/sign-language", tags=["Sign Language"])
adapter = SignLanguageAdapter()


class PredictRequest(BaseModel):
    frames: list[list[float]] = Field(..., min_length=1)


@router.get("/status")
def status():
    return adapter.status()


@router.post("/predict")
def predict(request: PredictRequest):
    arr = np.asarray(request.frames, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != 134:
        raise HTTPException(status_code=400, detail=f"Expected frames shaped [T,134], got {arr.shape}")
    try:
        return adapter.predict(arr)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
