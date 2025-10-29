from pydantic import BaseModel
from typing import Optional, List, Literal

Status = Literal["QUEUED","PROCESSING","READY","FAILED"]

class DocCreateResponse(BaseModel):
    document_id: str
    status: Status

class DocItem(BaseModel):
    document_id: str
    filename: str
    status: Status
    page_count: int = 0
    chunk_count: int = 0
    created_at: str
    updated_at: str

class DocListResponse(BaseModel):
    items: List[DocItem]
