# app/services/extractor.py

"""
Simple text extractor for PDFs and text files.

Provides:
    - extract_text_pages(file_path)  -> list[str]
    - extract_text_from_file(file_path) -> dict
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None  # We'll show a clear error message later


# ---------------------------
#   Helper extractors
# ---------------------------

def _extract_from_pdf(path: Path) -> List[str]:
    """Extracts text page-by-page from a PDF."""
    if PyPDF2 is None:
        raise RuntimeError(
            "PyPDF2 not installed. Install with: pip install PyPDF2"
        )

    pages = []
    with path.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append(text)
    return pages


def _extract_from_txt(path: Path) -> List[str]:
    """Treat .txt or .md as a single 'page'."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = text.strip()
    return [text] if text else []


# ---------------------------
#   Public API (EXPECTED)
# ---------------------------

def extract_text_pages(file_path: str | os.PathLike) -> List[str]:
    """
    Main extractor used in pipeline.py.
    Returns a list of page texts.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()

    if ext == ".pdf":
        return _extract_from_pdf(path)
    elif ext in {".txt", ".md"}:
        return _extract_from_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_text_from_file(file_path: str | os.PathLike) -> Dict:
    """
    This function is required by routes_documents.py.
    Returns:
        {
            "pages": [...],
            "num_pages": int
        }
    """
    pages = extract_text_pages(file_path)
    return {
        "pages": pages,
        "num_pages": len(pages)
    }
