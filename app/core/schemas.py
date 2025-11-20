# app/core/schemas.py

from typing import List, Dict, Literal, Optional
from pydantic import BaseModel, Field


# ---------- Basic text chunk from a document ----------

class TextChunk(BaseModel):
    text: str
    page: int = 0
    path: str = ""   # file path or URL


# ---------- Retrieved chunk (for query/answer/summarize) ----------

class RetrievedChunk(BaseModel):
    text: str
    score: float = 0.0
    meta: Dict[str, object] = Field(default_factory=dict)


# ---------- /v1/upload responses ----------

class UploadResponse(BaseModel):
    ok: bool = True
    filename: str
    chunks_indexed: int
    collection_info: Optional[Dict[str, object]] = None
    message: str = "Indexed successfully"


# ---------- /v1/query ----------

class QueryRequest(BaseModel):
    query: str
    top_k: int = 4
    mode: Literal["semantic", "hybrid", "keyword"] = "semantic"


class QueryResponse(BaseModel):
    query: str
    results: List[RetrievedChunk]


# ---------- /v1/answer ----------

class AnswerRequest(BaseModel):
    question: str
    top_k: int = 4
    mode: Literal["semantic", "hybrid", "keyword"] = "semantic"
    provider: Literal["openai", "ollama"] = "openai"
    model: str = "gpt-4o-mini"


class AnswerResponse(BaseModel):
    answer: str
    used_chunks: List[RetrievedChunk]


# ---------- /v1/summarize ----------

class SummarizeRequest(BaseModel):
    max_chunks: int = 50


class SummarizeResponse(BaseModel):
    summary: str
