# app/api/routes_quiz.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import random, re
from app.services.retriever import retrieve_chunks

router = APIRouter(tags=["quiz"])

class QuizReq(BaseModel):
    topic: str = ""
    num_questions: int = Field(5, ge=3, le=20)
    mode: str = Field("hybrid", pattern="^(hybrid|semantic)$")
    difficulty: str = Field("easy", pattern="^(easy|med|hard)$")

@router.post("/quiz")
def quiz(req: QuizReq):
    q = req.topic.strip() or "key facts overview"
    hits = retrieve_chunks(q, top_k=max(10, req.num_questions*3), mode=req.mode)
    if not hits:
        raise HTTPException(404, "No content indexed. Upload a document first.")

    # naive noun-phrase based MCQs
    text = " ".join([h["text"] for h in hits])
    cands = list({w for w in re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", text)})[:100]
    if len(cands) < req.num_questions:
        cands = (cands + ["Concept", "Method", "System", "Process", "Model"])[:100]

    out: List[Dict[str, Any]] = []
    for i in range(req.num_questions):
        correct = random.choice(cands)
        opts = {correct}
        while len(opts) < 4:
            opts.add(random.choice(cands))
        options = list(opts)
        random.shuffle(options)
        out.append({
            "q": f"Which term best fits the context of the uploaded documents?",
            "options": options,
            "answer": correct,
        })
    return {"topic": req.topic or "general", "items": out}
