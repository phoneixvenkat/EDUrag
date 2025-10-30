# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_documents import router as docs_router
from app.api.routes_query import router as query_router
from app.api.routes_answer import router as answer_router
from app.api.routes_quiz import router as quiz_router

app = FastAPI(title="EduRAG API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(docs_router,  prefix="/v1")
app.include_router(query_router, prefix="/v1")
app.include_router(answer_router, prefix="/v1")
app.include_router(quiz_router,   prefix="/v1")
