from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any

from app.services.retriever import retrieve
from app.services.generator import generate_answer

router = APIRouter(tags=["answer"])

class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(8, ge=1, le=50)
    mode: Literal["semantic", "hybrid"] = "hybrid"
    alpha: float = Field(0.6, ge=0.0, le=1.0)

@router.post("/answer")
def answer(req: AnswerRequest):
    passages = retrieve(req.question, top_k=req.top_k, mode=req.mode, alpha=req.alpha)
    ctx = " ".join([p["text"] for p in passages])[:3000]
    ans = generate_answer(req.question, ctx)
    # include compact sources
    sources = [
        {
            "source": p.get("meta", {}).get("source"),
            "page": p.get("meta", {}).get("page"),
            "preview": p["text"][:220]
        }
        for p in passages[:3]
    ]
    return {"answer": ans, "sources": sources}
