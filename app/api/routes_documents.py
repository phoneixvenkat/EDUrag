# app/api/routes_documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Any, Tuple
import uuid
import shutil
import os

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.vectorstore import vs_add, vs_list_docs, vs_delete_doc, vs_clear

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(tags=["documents"])

class UploadResponse(BaseModel):
    filename: str
    saved_to: str
    chunks_indexed: int
    vector_ids: List[str]
    vector_stats: Dict[str, Any]

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(415, f"Unsupported type: {file.content_type}")

    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Unified extractor returns: text, [(start,end,page)]
    text, page_spans = extract_text(dest, mime=file.content_type)
    if not text.strip():
        raise HTTPException(400, "No extractable text in the file.")

    chunks = chunk_text(text)
    # attach page numbers by span lookup
    def page_of(start_idx: int) -> int:
        for (s,e,p) in page_spans:
            if s <= start_idx < e: 
                return p
        return -1

    docs = []
    for c in chunks:
        meta = {
            "source": file.filename,
            "path": str(dest),
            "page": page_of(c["start"]),
        }
        docs.append({"id": str(uuid.uuid4()), "text": c["text"], "meta": meta})

    vec_ids, stats = vs_add(docs)
    return UploadResponse(
        filename=file.filename,
        saved_to=str(dest),
        chunks_indexed=len(docs),
        vector_ids=vec_ids,
        vector_stats=stats,
    )

class DocList(BaseModel):
    documents: List[Dict[str, Any]]

@router.get("/documents", response_model=DocList)
def list_documents():
    return {"documents": vs_list_docs()}

class DeleteReq(BaseModel):
    path: str

@router.post("/documents/delete")
def delete_document(req: DeleteReq):
    ok = vs_delete_doc(req.path)
    if not ok:
        raise HTTPException(404, "Document not found in index.")
    return {"ok": True}

@router.post("/documents/clear")
def clear_all():
    vs_clear()
    return {"ok": True}
