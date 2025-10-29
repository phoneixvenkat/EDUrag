import uuid
from app.core.config import settings
from app.services.extractor import extract_text_pages
from app.services.chunker import chunk_pages
from app.services.embeddings import embed_texts
from app.services.vectorstore import get_collection
from app.services.bm25_index import add_chunks as bm25_add_chunks

def process_document(path: str, sha256: str) -> dict:
    pages = extract_text_pages(path)
    chunks = chunk_pages(pages, settings.max_chunk_tokens, settings.chunk_overlap)
    if not chunks:
        return {"document_id": str(uuid.uuid4()), "page_count": len(pages), "chunk_count": 0}

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metas = [{"page": c["page"], "sha256": sha256, "chunk_id": c["chunk_id"]} for c in chunks]

    # embeddings → vector DB
    embs = embed_texts(texts, settings.embedding_model_name)
    col = get_collection()
    col.add(ids=ids, documents=texts, metadatas=metas, embeddings=embs)

    # also update BM25 local index
    bm25_add_chunks(texts, metas)

    return {
        "document_id": str(uuid.uuid4()),
        "page_count": len(pages),
        "chunk_count": len(chunks),
    }
