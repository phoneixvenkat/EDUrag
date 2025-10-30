# app/services/retriever.py
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import re

from app.services.vectorstore import vs_query, COLL

def _tokenize(txt: str) -> List[str]:
    return re.findall(r"\w+", txt.lower())

def retrieve_chunks(query: str, top_k: int = 8, mode: str = "hybrid") -> List[Dict[str, Any]]:
    # vector
    v_hits = vs_query(query, top_k=top_k)
    if mode == "semantic":
        return v_hits

    # bm25 over the same candidate pool (quick heuristic)
    all_docs = COLL.get()  # small scale
    corpus = all_docs["documents"]
    if not corpus:
        return v_hits

    bm25 = BM25Okapi([_tokenize(c) for c in corpus])
    scores = bm25.get_scores(_tokenize(query))
    # pick top_k indices
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    b_hits = [{
        "id": all_docs["ids"][i],
        "text": all_docs["documents"][i],
        "meta": all_docs["metadatas"][i],
        "score": float(scores[i])
    } for i in idxs]

    # simple hybrid: interleave
    out = []
    for a, b in zip(v_hits, b_hits):
        out.append(a)
        out.append(b)
    # remove dupes by id
    seen, merged = set(), []
    for h in out:
        if h["id"] in seen: 
            continue
        merged.append(h); seen.add(h["id"])
        if len(merged) >= top_k: break
    return merged
