# app/api/routes_query.py

from fastapi import APIRouter

from app.core.schemas import QueryRequest, QueryResponse, RetrievedChunk
from app.services.pipeline import vs_query

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """
    Simple retrieval endpoint.
    """
    rows = vs_query(
        query=req.query,
        top_k=req.top_k,
        mode=req.mode,
    )

    chunks = [RetrievedChunk(**r) for r in rows]

    return QueryResponse(
        query=req.query,
        results=chunks,
    )
