# app/api/routes_query.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.retriever import retrieve_chunks

router = APIRouter(tags=["qa"])

class QueryReq(BaseModel):
    query: str
    top_k: int = 8
    mode: str = "hybrid"  # "hybrid" | "semantic"

@router.post("/query")
def query(req: QueryReq):
    hits = retrieve_chunks(req.query, top_k=req.top_k, mode=req.mode)
    return {"query": req.query, "results": hits}
