# app/api/routes_url.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup

router = APIRouter()

class URLBody(BaseModel):
    url: HttpUrl

@router.post("/url")
def add_url(body: URLBody):
    try:
        r = requests.get(str(body.url), timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n")
        # Process text: chunk, embed, and store in Chroma DB
        # (You should call your existing chunking/embedding function here)
        return {"ok": True, "chars": len(text)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
