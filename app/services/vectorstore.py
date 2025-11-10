# app/services/vectorstore.py
from __future__ import annotations
import os, logging
from typing import List, Dict, Any, Tuple
from uuid import uuid4
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

log = logging.getLogger("app.vectorstore")

CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "edurag")
EMBED_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

_CLIENT = None
_COLL = None
_EMB: SentenceTransformer | None = None

def _client():
    global _CLIENT
    if _CLIENT is None:
        os.makedirs(CHROMA_DIR, exist_ok=True)
        _CLIENT = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False))
        log.info("Using Chroma at %s", CHROMA_DIR)
    return _CLIENT

def _collection():
    global _COLL
    if _COLL is None:
        _COLL = _client().get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
        log.info("Collection '%s' ready", COLLECTION_NAME)
    return _COLL

def _emb() -> SentenceTransformer:
    global _EMB
    if _EMB is None:
        _EMB = SentenceTransformer(EMBED_MODEL_NAME)
        log.info("Loaded embeddings: %s", EMBED_MODEL_NAME)
    return _EMB

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts: return []
    arr = _emb().encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return arr.tolist()

def vs_add(docs: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, Any]]:
    if not docs: return [], {"count": _collection().count(), "collection": COLLECTION_NAME}
    ids, texts, metas = [], [], []
    for d in docs:
        ids.append(d.get("id") or str(uuid4()))
        texts.append(d.get("text", ""))
        meta = d.get("meta", {}) or {}
        metas.append({k: (v if isinstance(v, (str, int, float, bool)) or v is None else str(v)) for k, v in meta.items()})
    vecs = embed_texts(texts)
    coll = _collection()
    coll.add(ids=ids, embeddings=vecs, metadatas=metas, documents=texts)
    return ids, {"count": coll.count(), "collection": COLLECTION_NAME}

def vs_list_docs() -> List[Dict[str, Any]]:
    coll = _collection()
    n = coll.count()
    if n == 0: return []
    got = coll.get(include=["metadatas"], limit=n)
    metas = got.get("metadatas", []) or []
    bucket: Dict[str, Dict[str, Any]] = {}
    for m in metas:
        path = (m or {}).get("path", "unknown")
        src = (m or {}).get("source", "unknown")
        if path not in bucket:
            bucket[path] = {"path": path, "count": 0, "sources": set()}
        bucket[path]["count"] += 1
        bucket[path]["sources"].add(src)
    out = []
    for v in bucket.values():
        out.append({"path": v["path"], "count": v["count"], "sources": sorted(list(v["sources"]))})
    return sorted(out, key=lambda x: x["path"])

def vs_delete_doc(path: str) -> bool:
    if not path: return False
    _collection().delete(where={"path": path})
    return True

def semantic_search(query: str, k: int = 6) -> List[Dict[str, Any]]:
    qv = embed_texts([query])[0]
    res = _collection().query(query_embeddings=[qv], n_results=k, include=["metadatas", "documents", "distances"])
    out: List[Dict[str, Any]] = []
    if res and res.get("documents"):
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        for t, m, d in zip(docs, metas, dists):
            out.append({"text": t, "meta": m, "score": float(1.0 - d)})
    return out

def vs_dump_all_docs(limit: int = 10000):
    got = _collection().get(limit=limit)
    docs = got.get("documents", []) or []
    metas = got.get("metadatas", []) or []
    ids = got.get("ids", []) or []
    rows = []
    for i, t in enumerate(docs):
        rows.append({"id": ids[i] if i < len(ids) else None, "text": t, "meta": metas[i] if i < len(metas) else {}})
    return rows
