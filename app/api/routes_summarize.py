# app/api/routes_summarize.py

from fastapi import APIRouter

from app.core.schemas import SummarizeRequest, SummarizeResponse
from app.services.generator import gen_summary

# This router gets mounted in main.py with prefix="/v1"
router = APIRouter(tags=["summarize"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    """
    Summarize the documents stored in the vectorstore.

    Uses at most `max_chunks` chunks from Chroma (from SummarizeRequest).
    """
    summary_text = gen_summary(max_chunks=req.max_chunks)
    return SummarizeResponse(summary=summary_text)
