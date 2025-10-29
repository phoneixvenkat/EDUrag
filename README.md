@"
# EduRAG – Learn from Your Documents

FastAPI + Streamlit + ChromaDB RAG app.  
Upload PDFs/TXT/URLs → Ask questions with citations → Generate quizzes.

## Run
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
$env:BACKEND_URL="http://127.0.0.1:8000"; streamlit run app/app_ui.py
