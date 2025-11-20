# app/main.py
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRoute

# --- Feature routers (must exist and expose `router = APIRouter()`) ---
from app.api.routes_documents import router as docs_router       # /v1/upload etc.
from app.api.routes_query import router as query_router          # /v1/query
from app.api.routes_answer import router as answer_router        # /v1/answer
from app.api.routes_summarize import router as summarize_router  # /v1/summarize



log = logging.getLogger("app.main")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# === App setup ===
app = FastAPI(title="EDUrag", version="1.0.0")

# CORS (open for dev — tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # e.g. ["http://127.0.0.1:5173"] for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root → UI
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")

# Health
@app.get("/v1/health")
def health():
    return {"status": "healthy"}

# Robust route lister (avoids "Internal Server Error" on mounts)
@app.get("/v1/routes")
def list_routes():
    items = []
    for r in app.router.routes:
        if isinstance(r, APIRoute):
            methods = sorted(list(r.methods or []))
        else:
            # Mounts / static routes etc. don't have .methods
            methods = []
        items.append({"path": getattr(r, "path", str(r)), "methods": methods})
    return {"routes": items}

# Mount feature routers
app.include_router(docs_router,      prefix="/v1")
app.include_router(query_router,     prefix="/v1")
app.include_router(answer_router,    prefix="/v1")
app.include_router(summarize_router, prefix="/v1")

# Serve static UI (expects web/index.html, web/script.js, web/styles.css)
app.mount("/ui", StaticFiles(directory="web", html=True), name="ui")

# Startup log
@app.on_event("startup")
def _startup():
    key_loaded = bool(os.getenv("OPENAI_API_KEY"))
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    log.info("🔑 OPENAI_API_KEY loaded? %s", key_loaded)
    log.info("🤖 MODEL_NAME: %s", model_name)
    log.info("✅ Server startup complete.")

# Optional: run directly via `python app/main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
