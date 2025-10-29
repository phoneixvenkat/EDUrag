from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any

from app.services.retriever import retrieve

router = APIRouter(tags=["query"])

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(8, ge=1, le=50)
    mode: Literal["semantic", "hybrid"] = "hybrid"
    alpha: float = Field(0.6, ge=0.0, le=1.0)

@router.post("/query")
def query_docs(req: QueryRequest):
    items = retrieve(req.query, top_k=req.top_k, mode=req.mode, alpha=req.alpha)
    return {
        "query": req.query,
        "top_k": req.top_k,
        "mode": req.mode,
        "alpha": req.alpha,
        "results": items,
    }
