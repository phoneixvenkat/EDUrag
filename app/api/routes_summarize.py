# app/api/routes_summarize.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.vectorstore import vs_dump_all_docs
from app.services.generator import summarize_text

router = APIRouter(prefix="/v1", tags=["summarize"])

class SummIn(BaseModel):
    max_tokens: int = 250

@router.post("/summarize")
def summarize(payload: SummIn) -> Dict[str, Any]:
    rows = vs_dump_all_docs()
    texts = [r["text"] for r in rows]
    if not texts:
        return {"summary": "", "note": "No documents indexed."}
    summary = summarize_text(texts, max_tokens=payload.max_tokens)
    return {"summary": summary, "chunks": len(texts)}
