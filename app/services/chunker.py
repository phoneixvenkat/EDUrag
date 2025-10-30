# app/services/chunker.py
from typing import List, Dict

def chunk_text(text: str, size: int = 500, overlap: int = 100) -> List[Dict]:
    out = []
    i = 0
    while i < len(text):
        j = min(i + size, len(text))
        out.append({"text": text[i:j], "start": i, "end": j})
        i = j - overlap
        if i <= 0: 
            i = j
    return out
