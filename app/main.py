# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()  # read .env at startup

app = FastAPI(title="RAG Backend", version="1.0")

# Routers
from app.api.routes_documents import router as docs_router
from app.api.routes_query import router as query_router
from app.api.routes_answer import router as answer_router
from app.api.routes_summarize import router as summarize_router

app.include_router(docs_router)        # /v1/upload, /v1/docs
app.include_router(query_router)       # /v1/query
app.include_router(answer_router)      # /v1/answer
app.include_router(summarize_router)   # /v1/summarize

# Quick startup print so you know the key is loaded
print("🔑 OPENAI_API_KEY loaded?", bool(os.getenv("OPENAI_API_KEY")))
