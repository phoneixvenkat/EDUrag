def chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 150):
    text = (text or "").replace("\r", " ").replace("\n", " ").strip()
    n = len(text)
    if n == 0:
        return []
    chunks = []
    i = 0
    while i < n:
        j = min(i + max_chars, n)
        chunk = text[i:j].strip()
        if chunk:
            chunks.append(chunk)
        if j == n:
            break
        i = max(0, j - overlap)
    return chunks
