# app/api/routes_documents.py

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.storage import save_and_index_pdf
from app.core.schemas import UploadResponse

router = APIRouter(tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    """
    1) Receive a PDF
    2) Save it to disk
    3) Extract + chunk + index via save_and_index_pdf
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename")

    upload_dir = Path("uploaded_files")
    upload_dir.mkdir(parents=True, exist_ok=True)

    target = upload_dir / file.filename

    # Save uploaded file to disk
    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Call storage pipeline
    try:
        result = save_and_index_pdf(target)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

    if not result.get("ok"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Unknown indexing error"),
        )

    return UploadResponse(
        ok=True,
        filename=result["filename"],
        chunks_indexed=result["chunks_indexed"],
        collection_info=result["collection_info"],
    )
