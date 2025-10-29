from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from app.services.vectorstore import vs_dump_all_docs
from app.services.generator import summarize_text

router = APIRouter(tags=["summarize"])

class SummarizeRequest(BaseModel):
    doc_id: Optional[str] = Field(None, description="Optional: future use if you track per-doc IDs")

@router.post("/summarize")
def summarize(req: SummarizeRequest):
    # simple: summarize everything we have (or extend to per-doc)
    full_text = " ".join([d["text"] for d in vs_dump_all_docs()])[:8000]
    if not full_text.strip():
        return {"summary": "No content indexed yet."}
    summ = summarize_text(full_text)
    return {"summary": summ}
