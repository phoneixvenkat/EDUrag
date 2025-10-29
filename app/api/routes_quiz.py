from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import re

from app.services.retriever import retrieve

router = APIRouter(tags=["quiz"])

class QuizRequest(BaseModel):
    topic: Optional[str] = None
    n: int = Field(5, ge=1, le=20)
    difficulty: Literal["easy", "med", "hard"] = "med"   # ← Pydantic v2-safe
    mode: Literal["hybrid", "semantic"] = "hybrid"
    alpha: float = Field(0.6, ge=0.0, le=1.0)

class QA(BaseModel):
    question: str
    answer: str
    source: Optional[str] = None
    page: Optional[int] = None

class QuizResponse(BaseModel):
    items: List[QA]

def _sentences(txt: str) -> List[str]:
    ss = re.split(r'(?<=[.!?])\s+', txt.strip())
    return [s for s in ss if len(s.split()) >= 6]

def _pick_token(s: str, difficulty: str) -> Optional[str]:
    toks = re.findall(r"\b[A-Za-z][A-Za-z\-]{4,}\b", s)
    if not toks:
        return None
    toks.sort(key=len, reverse=True)
    if difficulty == "easy":
        return toks[min(2, len(toks)-1)]
    if difficulty == "hard":
        return toks[0]
    return toks[min(1, len(toks)-1)]

@router.post("/quiz", response_model=QuizResponse)
def make_quiz(req: QuizRequest):
    query = req.topic or "retrieval augmented generation hybrid search embeddings bm25"
    items = retrieve(query, top_k=max(10, req.n * 2), mode=req.mode, alpha=req.alpha)
    pool = " ".join([x["text"] for x in items])[:8000]
    qs: List[QA] = []
    for s in _sentences(pool):
        token = _pick_token(s, req.difficulty)
        if not token:
            continue
        q = re.sub(rf"\b{re.escape(token)}\b", "_____", s, count=1)
        src = None
        page = None
        for it in items:
            if s[:40] in it["text"]:
                src = it.get("meta", {}).get("source")
                page = it.get("meta", {}).get("page")
                break
        qs.append(QA(question=f"Fill in the blank: {q}", answer=token, source=src, page=page))
        if len(qs) >= req.n:
            break
    if not qs:
        raise HTTPException(status_code=422, detail="Could not generate quiz")
    return QuizResponse(items=qs)
