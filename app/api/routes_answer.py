# app/api/routes_answer.py

from fastapi import APIRouter

from app.core.schemas import AnswerRequest, AnswerResponse, RetrievedChunk
from app.services.generator import gen_answer

router = APIRouter(tags=["answer"])


@router.post("/answer", response_model=AnswerResponse)
def answer(req: AnswerRequest):
    """
    LLM-grounded QA endpoint.
    Uses the vectorstore to retrieve chunks, then calls the selected LLM.
    """
    answer_text, ctx = gen_answer(
        question=req.question,
        top_k=req.top_k,
        mode=req.mode,
        provider=req.provider,
        model=req.model,
    )

    return AnswerResponse(
        answer=answer_text,
        used_chunks=[RetrievedChunk(**c) for c in ctx],
    )
