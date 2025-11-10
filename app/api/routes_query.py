# app/api/routes_query.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.retriever import retrieve_chunks

router = APIRouter(prefix="/v1", tags=["query"])

class QueryIn(BaseModel):
    query: str
    top_k: int = 6
    mode: str = "hybrid"

@router.post("/query")
def query(q: QueryIn) -> Dict[str, Any]:
    results = retrieve_chunks(q.query, top_k=q.top_k, mode=q.mode)
    return {"query": q.query, "results": results}
