# app/services/storage.py
from __future__ import annotations

import io
import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

try:
    # PyPDF2 is lightweight and already in most RAG stacks
    from PyPDF2 import PdfReader
except Exception as e:  # pragma: no cover
    PdfReader = None  # We'll raise a helpful error at runtime.

# Local services
from app.services.vectorstore import vs_add

log = logging.getLogger("app.services.storage")

# Where uploaded files live (git-ignored)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploaded_files")).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------- small utils ----------

def _read_pdf_text(pdf_path: Path) -> Tuple[str, int]:
    """Extracts plain text from a PDF and returns (text, page_count)."""
    if PdfReader is None:
        raise RuntimeError(
            "PyPDF2 is not installed. Please add 'PyPDF2' to requirements.txt and pip install."
        )
    reader = PdfReader(str(pdf_path))
    pages = len(reader.pages)
    parts: List[str] = []
    for i in range(pages):
        try:
            txt = reader.pages[i].extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            parts.append(txt)
    text = "\n\n".join(parts).strip()
    return text, pages


def _chunk_text(
    text: str,
    chunk_chars: int = 1400,
    overlap: int = 200,
) -> List[str]:
    """Simple, robust character-based chunker."""
    text = (text or "").strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_chars, n)
        # try to break on a nearby sentence boundary
        window = text[start:end]
        split_at = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("? "), window.rfind("! "))
        if split_at > 400:  # don't split too early
            end = start + split_at + 1

        chunks.append(text[start:end].strip())
        if end >= n:
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]


# ---------- main public API ----------

def save_and_index_pdf(
    file_path: str | Path,
    *,
    source: str = "upload",
    collection: Optional[str] = None,  # ignored here; collection is configured in vectorstore
) -> Dict[str, Any]:
    """
    Save (already on disk) PDF, extract text, chunk, embed, and index in Chroma.

    Returns:
        {
          "ok": true,
          "filename": "...",
          "pages": 12,
          "chunks_indexed": 25,
          "collection_info": {...}
        }
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Ensure the file is inside UPLOAD_DIR (copy if user gave a path from Downloads)
    if UPLOAD_DIR not in path.parents:
        target = UPLOAD_DIR / path.name
        if target.exists() and target.samefile(path) is False:
            target = UPLOAD_DIR / f"{target.stem}-{uuid.uuid4().hex[:8]}{target.suffix}"
        if not target.exists():
            target.write_bytes(path.read_bytes())
        path = target

    # Extract text
    text, pages = _read_pdf_text(path)
    if not text:
        return {
            "ok": False,
            "filename": path.name,
            "pages": pages,
            "chunks_indexed": 0,
            "error": "No text extracted from PDF (it may be scanned images). Enable OCR if needed.",
        }

    # Chunk
    chunks = _chunk_text(text, chunk_chars=1400, overlap=200)
    if not chunks:
        return {
            "ok": False,
            "filename": path.name,
            "pages": pages,
            "chunks_indexed": 0,
            "error": "Could not create chunks from extracted text.",
        }

    # Prepare docs for the vectorstore
    docs: List[Dict[str, Any]] = []
    for i, ch in enumerate(chunks, start=1):
        docs.append({
            "id": f"{path.name}:{i}",
            "text": ch,
            "meta": {
                "source": source,
                "path": str(path),
                "filename": path.name,
                "chunk_index": i,
                "chunks_total": len(chunks),
                "pages": pages,
            },
        })

    # Index
    ids, info = vs_add(docs)

    result = {
        "ok": True,
        "filename": path.name,
        "pages": pages,
        "chunks_indexed": len(ids),
        "collection_info": info,
    }
    log.info("Indexed PDF '%s' -> %s chunks", path.name, len(ids))
    return result
