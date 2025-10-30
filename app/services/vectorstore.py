# app/services/vectorstore.py
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# persistent DB
CLIENT = chromadb.PersistentClient(path="data/chroma", settings=Settings(anonymized_telemetry=False))
COLL = CLIENT.get_or_create_collection(name="edurag", metadata={"hnsw:space": "cosine"})
EMB = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def vs_add(docs: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, Any]]:
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metas = [d["meta"] for d in docs]
    vecs = EMB.encode(texts, normalize_embeddings=True).tolist()
    COLL.add(ids=ids, documents=texts, metadatas=metas, embeddings=vecs)
    return ids, {"count": COLL.count(), "collection": COLL.name}

def vs_query(q: str, top_k: int = 8) -> List[Dict[str, Any]]:
    emb = EMB.encode([q], normalize_embeddings=True).tolist()
    res = COLL.query(query_embeddings=emb, n_results=top_k)
    out = []
    for i in range(len(res["ids"][0])):
        out.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "meta": res["metadatas"][0][i],
            "score": float(res["distances"][0][i]) if "distances" in res else 0.0
        })
    return out

def vs_list_docs() -> List[Dict[str, Any]]:
    ids = COLL.get()["ids"]
    docs = COLL.get(ids=ids)
    rows = []
    for t, m in zip(docs["documents"], docs["metadatas"]):
        rows.append({"source": m.get("source"), "page": m.get("page"), "path": m.get("path")})
    uniq = {r["path"]: r for r in rows if r.get("path")}
    return list(uniq.values())

def vs_delete_doc(path: str) -> bool:
    ids = COLL.get()["ids"]
    docs = COLL.get(ids=ids)
    to_delete = [i for i, m in enumerate(docs["metadatas"]) if m.get("path") == path]
    if not to_delete:
        return False
    id_list = [docs["ids"][i] for i in to_delete]
    COLL.delete(ids=id_list)
    return True

def vs_clear():
    global COLL  # <-- move this to the top
    CLIENT.delete_collection(COLL.name)
    COLL = CLIENT.get_or_create_collection(name="edurag", metadata={"hnsw:space": "cosine"})
