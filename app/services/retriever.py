# app/services/retriever.py
from typing import List, Dict, Any
from app.services.vectorstore import semantic_search

def retrieve_chunks(query: str, top_k: int = 6, mode: str = "hybrid") -> List[Dict[str, Any]]:
    # For simplicity we just do semantic search; 'mode' kept for API compatibility
    return semantic_search(query, k=top_k)
