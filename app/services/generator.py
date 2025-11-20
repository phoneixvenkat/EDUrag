# app/services/generator.py

from __future__ import annotations

from typing import List, Dict, Any, Tuple

from app.services.pipeline import vs_query
from app.services.llm import chat_completion

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based only on the "
    "provided context. If the answer is not in the context, say you don't know."
)


def _build_context_string(chunks: List[Dict[str, Any]]) -> str:
    parts = []
    for i, ch in enumerate(chunks, start=1):
        text = ch.get("text", "")
        meta = ch.get("meta", {})
        src = meta.get("filename") or meta.get("source") or meta.get("path") or ""
        header = f"[Chunk {i}" + (f" from {src}]" if src else "]")
        parts.append(f"{header}\n{text}")
    return "\n\n".join(parts)


def gen_answer(
    question: str,
    top_k: int = 6,
    mode: str = "hybrid",
    provider: str | None = None,  # kept for compatibility, NOT used
    model: str | None = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Main QA pipeline:
    1) Retrieve chunks with vs_query
    2) Call LLM (Ollama via chat_completion)
    3) Return (answer, used_chunks)
    """
    retrieved = vs_query(query=question, top_k=top_k, mode=mode)

    if not retrieved:
        return "I don't know from the provided documents.", []

    ctx_text = _build_context_string(retrieved)

    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Context:\n{ctx_text}\n\n"
                "Give a clear answer in 3–6 bullet points."
            ),
        },
    ]

    answer = chat_completion(messages=messages, model=model)
    return answer, retrieved


def gen_summary(max_chunks: int = 10, model: str | None = None) -> str:
    """
    Summarize top-k chunks from the vectorstore.
    Used by /v1/summarize.
    """
    retrieved = vs_query(
        query="Summarize the main ideas of this document.",
        top_k=max_chunks,
        mode="semantic",
    )

    if not retrieved:
        return "No documents found to summarize."

    ctx_text = _build_context_string(retrieved)

    messages = [
        {"role": "system", "content": "You create concise summaries from context only."},
        {
            "role": "user",
            "content": (
                "Create a short summary (3–6 bullet points) of the following content:\n\n"
                f"{ctx_text}"
            ),
        },
    ]

    summary = chat_completion(messages=messages, model=model)
    return summary
