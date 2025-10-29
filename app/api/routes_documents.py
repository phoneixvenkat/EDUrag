# app/api/routes_documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List, Tuple
import os

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.vectorstore import vs_add_documents, vs_stats
from app.services.bm25_index import bm25_add_documents

router = APIRouter(tags=["documents"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory registry (for /documents listing)
_DOCS: List[Dict[str, Any]] = []  # {filename, path, chunks}

def _coerce_extract_result(res) -> Tuple[str, List[tuple]]:
    """
    Accepts res as: text | (text,) | (text, spans) | (text, spans, ...)
    Returns (text, spans) where spans is [(start, end, page_no), ...] or a single-span default.
    """
    # Only text
    if not isinstance(res, tuple):
        text = str(res or "")
        return text, [(0, len(text), 1)]
    # Tuple-like
    if len(res) == 0:
        return "", [(0, 0, 1)]
    if len(res) == 1:
        text = res[0] or ""
        return text, [(0, len(text), 1)]
    # len >= 2: take the first two
    text = res[0] or ""
    spans = res[1] or []
    # Normalize spans shape
    if not isinstance(spans, list) or (spans and not isinstance(spans[0], tuple)):
        # fallback to single-span
        spans = [(0, len(text), 1)]
    return text, spans

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "text/plain"}:
        raise HTTPException(status_code=415, detail="Only PDF or TXT supported")

    path = os.path.join(UPLOAD_DIR, file.filename)
    # Save the upload once
    blob = await file.read()
    with open(path, "wb") as f:
        f.write(blob)

    # Extract (be tolerant to different return shapes)
    res = extract_text(path, mime=file.content_type)
    text, page_spans = _coerce_extract_result(res)

    if not text.strip():
        raise HTTPException(status_code=422, detail="No text extracted from document.")

    # Chunk
    chunks = chunk_text(text, max_chars=1200, overlap=150)

    # Map chunk positions → pages (best effort)
    def page_for_segment(start_char: int, end_char: int) -> int:
        best_page, best_overlap = 1, 0
        for s, e, p in page_spans:
            ov = max(0, min(end_char, e) - max(start_char, s))
            if ov > best_overlap:
                best_overlap, best_page = ov, p
        return best_page

    metadatas = []
    offset = 0
    for ch in chunks:
        start = text.find(ch, offset)
        if start < 0:
            start = offset
        end = start + len(ch)
        page = page_for_segment(start, end)
        metadatas.append({"source": file.filename, "page": page})
        offset = end

    ids = vs_add_documents(chunks, metadatas=metadatas)
    bm25_add_documents(chunks, metadatas)

    _DOCS.append({"filename": file.filename, "path": path, "chunks": len(chunks)})

    return {
        "filename": file.filename,
        "saved_to": path,
        "chunks_indexed": len(chunks),
        "vector_ids": ids,
        "vector_stats": vs_stats(),
    }

@router.get("/documents")
def list_documents():
    return {
        "documents": _DOCS,
        "vector_stats": vs_stats(),
    }
