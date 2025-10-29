from typing import List, Literal
from app.services.vectorstore import vs_query
from app.services.bm25_index import bm25_query

def _norm(items, higher_is_better: bool):
    if not items:
        return items
    vals = [x["score"] for x in items]
    lo, hi = min(vals), max(vals)
    for x in items:
        if hi == lo:
            x["_norm"] = 0.5
        else:
            v = x["score"]
            x["_norm"] = (v - lo) / (hi - lo) if higher_is_better else (hi - v) / (hi - lo)
    return items

def retrieve(query: str, top_k: int = 8, mode: Literal["semantic", "hybrid"]="hybrid", alpha: float=0.6):
    if mode == "semantic":
        dense = vs_query(query, top_k=top_k)  # distance (lower is better)
        dense = _norm(dense, higher_is_better=False)
        for d in dense:
            d["score"] = d["_norm"]
        dense.sort(key=lambda x: x["score"], reverse=True)
        return dense[:top_k]

    dense = _norm(vs_query(query, top_k=top_k), higher_is_better=False)
    lex = _norm(bm25_query(query, top_k=top_k), higher_is_better=True)

    fused = {}
    for x in dense:
        fused[x["text"]] = {"text": x["text"], "meta": x.get("meta", {}), "dense": x["_norm"], "lex": 0.0}
    for x in lex:
        if x["text"] in fused:
            fused[x["text"]]["lex"] = x["_norm"]
        else:
            fused[x["text"]] = {"text": x["text"], "meta": x.get("meta", {}), "dense": 0.0, "lex": x["_norm"]}

    items = list(fused.values())
    for it in items:
        it["score"] = alpha * it["dense"] + (1 - alpha) * it["lex"]
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:top_k]
