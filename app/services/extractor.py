from PyPDF2 import PdfReader

def extract_text(path: str, mime: str) -> str:
    if mime == "text/plain" or path.lower().endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    # PDF
    reader = PdfReader(path)
    out = []
    for page in reader.pages:
        try:
            out.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(out)
