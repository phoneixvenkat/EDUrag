# app/services/embeddings.py
"""
Local embedding utilities.

This module exposes:
    - embed_texts(texts: List[str]) -> List[List[float]]
    - embed_text(text: str) -> List[float]

Used by pipeline / evaluation code instead of remote OpenAI embeddings.
"""

from __future__ import annotations

from typing import List

import torch
from transformers import AutoTokenizer, AutoModel

from app.core.config import settings


# Use the model name from .env or default to MiniLM
_EMBEDDING_MODEL_NAME = getattr(settings, "embeddings_model", None) or "all-MiniLM-L6-v2"

_tokenizer = None
_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_model():
    """
    Lazy-load the HuggingFace model & tokenizer once.
    """
    global _tokenizer, _model

    if _tokenizer is not None and _model is not None:
        return

    _tokenizer = AutoTokenizer.from_pretrained(_EMBEDDING_MODEL_NAME)
    _model = AutoModel.from_pretrained(_EMBEDDING_MODEL_NAME)
    _model.to(_device)
    _model.eval()


@torch.no_grad()
def _encode_batch(texts: List[str]) -> List[List[float]]:
    """
    Encode a batch of texts into sentence embeddings using mean pooling.
    """
    _load_model()

    # Replace empty or None texts to avoid crashes
    clean_texts = [t if (t is not None and t.strip()) else "" for t in texts]

    encoded = _tokenizer(
        clean_texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    encoded = {k: v.to(_device) for k, v in encoded.items()}

    outputs = _model(**encoded)
    last_hidden_state = outputs.last_hidden_state  # (batch, seq_len, hidden_dim)
    attention_mask = encoded["attention_mask"]     # (batch, seq_len)

    # Mean pooling with mask
    mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    sum_embeddings = (last_hidden_state * mask_expanded).sum(1)
    sum_mask = mask_expanded.sum(1).clamp(min=1e-9)
    embeddings = sum_embeddings / sum_mask

    # Convert to plain Python lists
    return embeddings.cpu().tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Public API: embed a list of texts.

    This is what pipeline.py expects to import:
        from app.services.embeddings import embed_texts
    """
    if not texts:
        return []

    # If a single string is accidentally passed, wrap it
    if isinstance(texts, str):
        texts = [texts]

    return _encode_batch(texts)


def embed_text(text: str) -> List[float]:
    """
    Convenience function for a single text.
    """
    if text is None:
        text = ""
    return embed_texts([text])[0]
