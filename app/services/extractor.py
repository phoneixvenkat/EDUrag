# app/services/extractor.py
from typing import Tuple, List
from pathlib import Path
from PyPDF2 import PdfReader

def extract_text(path: Path, mime: str) -> Tuple[str, List[tuple]]:
    """
    Returns:
      full_text (str)
      page_spans: list of (start_idx, end_idx, page_no)
    """
    text = ""
    spans = []
    if mime == "application/pdf":
        reader = PdfReader(str(path))
        cursor = 0
        for i, page in enumerate(reader.pages, start=1):
            t = page.extract_text() or ""
            start, end = cursor, cursor + len(t)
            spans.append((start, end, i))
            text += t
            cursor = end
    else:
        t = path.read_text(encoding="utf-8", errors="ignore")
        text, spans = t, [(0, len(t), 1)]
    return text, spans
