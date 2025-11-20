# app/services/retriever.py
from typing import List, Dict, Any
from app.services.vectorstore import semantic_search

def retrieve_chunks(query: str, k: int = 6) -> List[Dict[str, Any]]:
    return semantic_search(query, k=k)
