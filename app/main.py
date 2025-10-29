from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_documents import router as docs_router
from app.api.routes_query import router as query_router
from app.api.routes_answer import router as answer_router
from app.api.routes_quiz import router as quiz_router
from app.api.routes_summarize import router as summarize_router

app = FastAPI(title="EduRAG API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "EduRAG API",
        "version": "0.4.0",
        "docs": "/docs",
        "health": "/healthz",
        "endpoints": ["/v1/upload", "/v1/query", "/v1/answer", "/v1/quiz", "/v1/summarize", "/v1/documents"],
    }

@app.get("/healthz")
def healthz():
    return {"ok": True}

# Mount routers under /v1
app.include_router(docs_router, prefix="/v1")
app.include_router(query_router, prefix="/v1")
app.include_router(answer_router, prefix="/v1")
app.include_router(quiz_router, prefix="/v1")
app.include_router(summarize_router, prefix="/v1")
