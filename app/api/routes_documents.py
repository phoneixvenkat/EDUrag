# app/api/routes_documents.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any, List
from app.services.extractor import extract_docs_from_upload
from app.services.vectorstore import vs_add, vs_list_docs

router = APIRouter(prefix="/v1", tags=["documents"])

@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    docs = await extract_docs_from_upload(file)   # List[{"id","text","meta"}]
    if not docs:
        raise HTTPException(status_code=400, detail="No text extracted from file")
    ids, info = vs_add(docs)
    return {"ok": True, "filename": file.filename, "chunks_indexed": len(ids), "collection_info": info}

@router.get("/docs")
def list_docs() -> List[Dict[str, Any]]:
    return vs_list_docs()
