# app/services/llm.py
"""
Offline "LLM" stub for the RAG app.

We can't reliably use OpenAI or Ollama, so:
- chat_completion(...) builds a simple, extractive answer
- It formats the answer into 3–6 bullet points from the retrieved context.

This keeps:
- generator.py unchanged
- routes_answer unchanged
- UI unchanged (still shows provider + model dropdown)
"""

from __future__ import annotations

from typing import List, Dict


def _to_bullets(text: str, min_len: int = 20, max_points: int = 6) -> str:
    """
    Turn a block of text into 3–6 bullet points by splitting into sentences.
    No AI, just simple string ops.
    """
    # Normalize spaces
    t = " ".join(text.split())
    if not t:
        return "• I don't know from the provided documents."

    # Rough sentence split
    import re

    sentences = re.split(r"(?<=[\.\?\!])\s+", t)
    # Filter very short bits & meta instruction lines
    sentences = [
        s.strip()
        for s in sentences
        if len(s.strip()) >= min_len and "Give a clear answer" not in s
    ]

    if not sentences:
        return "• I don't know from the provided documents."

    # Take up to max_points
    sentences = sentences[:max_points]

    bullets = "\n".join(f"• {s}" for s in sentences)
    return bullets


def chat_completion(
    messages: List[Dict[str, str]],
    model: str | None = None,
) -> str:
    """
    Drop-in replacement for a real LLM.

    Parameters
    ----------
    messages : list of {"role": "system"|"user"|"assistant", "content": str}
    model    : optional model name (ignored, but accepted for compatibility)

    Returns
    -------
    str : bullet-point answer text
    """

    # Concatenate all messages into one "prompt"
    parts: List[str] = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if not content:
            continue
        parts.append(content)

    full_prompt = "\n\n".join(parts).strip()
    if not full_prompt:
        return "• I don't know from the provided documents."

    # Take a window near the end (likely contains context + question)
    window_size = 1000
    snippet = full_prompt[-window_size:] if len(full_prompt) > window_size else full_prompt

    return _to_bullets(snippet)


def embed_text(texts: List[str]) -> List[List[float]]:
    """
    Dummy embedding function so any legacy import doesn't crash.
    Real embeddings are done in app/services/embeddings.py.
    """
    if isinstance(texts, str):
        texts = [texts]
    dim = 384
    return [[0.0] * dim for _ in texts]
