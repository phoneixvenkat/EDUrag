# app/services/extractor.py
from typing import List, Dict, Any
from uuid import uuid4
from fastapi import UploadFile
from pypdf import PdfReader

async def extract_docs_from_upload(file: UploadFile) -> List[Dict[str, Any]]:
    # Read the bytes
    data = await file.read()
    # Save to temp in-memory and parse with pypdf
    from io import BytesIO
    pdf = PdfReader(BytesIO(data))
    docs: List[Dict[str, Any]] = []
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue
        docs.append({
            "id": str(uuid4()),
            "text": text,
            "meta": {"source": "upload", "path": file.filename, "page": i}
        })
    return docs
