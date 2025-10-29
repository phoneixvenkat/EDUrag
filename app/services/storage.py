from pathlib import Path
import hashlib, shutil, time
from app.core.config import settings

def ensure_dirs():
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)

def save_upload(file) -> str:
    ensure_dirs()
    out = Path(settings.upload_dir) / file.filename
    with out.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return str(out)

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
