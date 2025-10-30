# app/api/routes_answer.py
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from transformers import pipeline
from app.services.retriever import retrieve_chunks

router = APIRouter(tags=["qa"])

MODEL = os.getenv("ANSWER_MODEL", "sshleifer/distilbart-cnn-12-6")  # light & fast
SUM = pipeline("summarization", model=MODEL)

class AnswerReq(BaseModel):
    question: str
    top_k: int = 8
    mode: str = "hybrid"

@router.post("/answer")
def answer(req: AnswerReq):
    hits = retrieve_chunks(req.question, top_k=req.top_k, mode=req.mode)
    context = "\n".join([h["text"] for h in hits])[:4000]  # keep short for speed

    if not context.strip():
        raise HTTPException(404, "No context found. Upload a document first.")

    summary = SUM(context, max_length=160, min_length=60, do_sample=False)[0]["summary_text"]

    return {
        "answer": summary,
        "sources": [
            {
                "source": h["meta"]["source"],
                "page": h["meta"].get("page", -1),
                "score": h["score"],
                "snippet": h["text"][:160]
            } for h in hits
        ],
    }
