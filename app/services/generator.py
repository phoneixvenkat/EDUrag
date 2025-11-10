# app/services/generator.py
from typing import List
from app.services.llm import chat

SYS_RAG = (
    "You are a helpful assistant. Answer ONLY using the provided context. "
    "If the answer isn't in the context, say you don't know."
)

def _mk_context_block(contexts: List[str], max_chars: int = 8000) -> str:
    joined, used = "", 0
    for c in contexts:
        if used + len(c) + 2 > max_chars: break
        joined += f"- {c}\n"
        used += len(c) + 2
    return joined.strip()

def gen_answer(question: str, contexts: List[str]) -> str:
    ctx_block = _mk_context_block(contexts)
    messages = [
        {"role": "system", "content": SYS_RAG},
        {"role": "user", "content": f"Context:\n{ctx_block}\n\nQuestion: {question}\nAnswer succinctly."}
    ]
    return chat(messages)

def summarize_text(chunks: List[str], max_tokens: int = 250) -> str:
    ctx_block = _mk_context_block(chunks)
    messages = [
        {"role": "system", "content": "You are a concise scientific summarizer."},
        {"role": "user", "content": f"Summarize the following corpus in <= {max_tokens} tokens:\n{ctx_block}"}
    ]
    return chat(messages)
