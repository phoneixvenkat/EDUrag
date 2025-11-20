from __future__ import annotations
from typing import List


def chunk_text(
    text: str,
    max_chars: int = 800,
    overlap: int = 100,
) -> List[str]:
    if not text or not text.strip():
        return []

    text = text.strip()
    chunks: List[str] = []

    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        start = max(0, end - overlap)

    return chunks


def chunk_pages(
    pages: List[str],
    max_chars: int = 800,
    overlap: int = 100,
) -> List[str]:
    all_chunks: List[str] = []

    for page in pages:
        if page and page.strip():
            page_chunks = chunk_text(page, max_chars=max_chars, overlap=overlap)
            all_chunks.extend(page_chunks)

    return all_chunks
