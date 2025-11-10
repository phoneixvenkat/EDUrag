# app/api/routes_answer.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.retriever import retrieve_chunks
from app.services.generator import gen_answer

router = APIRouter(prefix="/v1", tags=["answer"])

class AnswerIn(BaseModel):
    question: str
    top_k: int = 6
    mode: str = "hybrid"

@router.post("/answer")
def answer_endpoint(payload: AnswerIn) -> Dict[str, Any]:
    ctx = retrieve_chunks(payload.question, top_k=payload.top_k, mode=payload.mode)
    contexts = [c["text"] for c in ctx]
    answer = gen_answer(payload.question, contexts)
    return {"question": payload.question, "answer": answer, "sources": ctx}
