# app/services/pipeline.py
"""
Pipeline handles:
- hybrid search (semantic + keyword)
- semantic-only search
- keyword-only search

Exports:
    - vs_query(query: str, top_k: int = 6, mode: str = "hybrid") -> list[dict]
"""

from __future__ import annotations

from typing import List, Dict, Any

from app.services.vectorstore import semantic_query
from app.services.bm25_index import query as bm25_query


def _hybrid_merge(
    semantic: List[Dict[str, Any]],
    keyword: List[Dict[str, Any]],
    top_k: int,
) -> List[Dict[str, Any]]:
    """Merge semantic + BM25 results with normalized scores."""

    # Normalize semantic scores
    if semantic:
        max_sem = max(r["score"] for r in semantic)
        for r in semantic:
            r["score"] = r["score"] / (max_sem or 1.0)

    # Normalize BM25 scores
    if keyword:
        max_kw = max(r["score"] for r in keyword)
        for r in keyword:
            r["score"] = r["score"] / (max_kw or 1.0)

    # Tag mode for debugging
    for r in semantic:
        r["meta"]["mode"] = "semantic"
    for r in keyword:
        r["meta"]["mode"] = "keyword"

    # Merge
    merged = semantic + keyword

    # Sort by score descending
    merged.sort(key=lambda x: x["score"], reverse=True)

    return merged[:top_k]


def vs_query(query: str, top_k: int = 6, mode: str = "hybrid") -> List[Dict[str, Any]]:
    """
    Perform vectorstore retrieval.

    mode = "semantic" | "keyword" | "hybrid"
    """
    mode = mode.lower()

    # --- 1) Semantic search ---
    semantic_results = semantic_query(query, top_k=top_k)

    # --- 2) Keyword/BM25 search ---
    keyword_results = bm25_query(query, top_k=top_k)

    # --- 3) Mode selection ---
    if mode == "semantic":
        return semantic_results

    if mode == "keyword":
        return keyword_results

    # --- 4) Hybrid merge ---
    return _hybrid_merge(semantic_results, keyword_results, top_k)
