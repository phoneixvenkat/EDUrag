# app/api/routes_health.py
from __future__ import annotations

import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from app.services.vectorstore import _collection  # type: ignore

router = APIRouter(prefix="/v1", tags=["health"])

class HealthResp(BaseModel):
    ok: bool
    openai_key_loaded: bool
    collection: str
    count: int
    model: str

@router.get("/health", response_model=HealthResp)
def health() -> HealthResp:
    openai_key_loaded = bool(os.getenv("OPENAI_API_KEY"))
    coll = _collection()
    return HealthResp(
        ok=True,
        openai_key_loaded=openai_key_loaded,
        collection=coll.name,
        count=coll.count(),
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    )
