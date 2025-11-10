# app/services/llm.py
import os
from typing import List, Dict
from openai import OpenAI

_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        # OPENAI_API_KEY must be in env or .env (loaded by main.py)
        _client = OpenAI()
    return _client

def chat(messages: List[Dict[str, str]], model: str = None) -> str:
    resp = _get_client().chat.completions.create(
        model=model or _MODEL,
        messages=messages,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
