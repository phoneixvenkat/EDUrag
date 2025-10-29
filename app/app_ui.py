from __future__ import annotations
import os, requests, json
import streamlit as st
from typing import Dict, Any, Tuple

st.set_page_config(page_title="EduRAG – Learn from your documents", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

# Base URL without /v1
BACKEND_URL  = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT_SECS = int(os.getenv("BACKEND_TIMEOUT", "60"))

def _err(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"status_code": resp.status_code, "text": resp.text}

@st.cache_data(ttl=5)
def healthz() -> bool:
    try:
        r = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
        r.raise_for_status()
        return r.json().get("ok", False)
    except Exception:
        return False

def post_json(path: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=TIMEOUT_SECS)
        r.raise_for_status()
        return True, r.json()
    except requests.HTTPError:
        return False, _err(r)
    except Exception as e:
        return False, {"detail": str(e)}

def post_file(path: str, file_name: str, data: bytes, mime: str) -> Tuple[bool, Dict[str, Any]]:
    files = {"file": (file_name, data, mime)}
    try:
        r = requests.post(f"{BACKEND_URL}{path}", files=files, timeout=TIMEOUT_SECS)
        r.raise_for_status()
        return True, r.json()
    except requests.HTTPError:
        return False, _err(r)
    except Exception as e:
        return False, {"detail": str(e)}

# Styles
st.markdown("""
<style>
  .app-title { font-size: 2rem; font-weight: 800; letter-spacing: .2px; }
  .pill { padding: .45rem .7rem; border-radius: .6rem; font-weight: 600; display:inline-block; }
  .ok { background: #123d29; border: 1px solid #1f7a55; }
  .bad { background: #3b0f12; border: 1px solid #a03e46; }
  .foot { font-size: .85rem; opacity: .7; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Main Menu")
    page = st.radio("", ["Upload Document", "Enter URL", "Ask Question", "Quiz Mode", "Documents"], label_visibility="collapsed")
    st.markdown(f'<div class="foot">Backend: <a href="{BACKEND_URL}" target="_blank">{BACKEND_URL}</a></div>', unsafe_allow_html=True)

st.markdown('<div class="app-title">EduRAG – Learn from your documents</div>', unsafe_allow_html=True)
if healthz():
    st.markdown('<span class="pill ok">✅ Backend is ready</span>', unsafe_allow_html=True)
else:
    st.markdown(f'<span class="pill bad">🚫 Backend unreachable at {BACKEND_URL}</span>', unsafe_allow_html=True)
    st.stop()

st.divider()

if page == "Upload Document":
    st.subheader("📤 Upload PDF/TXT")
    up = st.file_uploader("Choose a file", type=["pdf", "txt"])
    if up:
        name = up.name
        data = up.getvalue()
        mime = "application/pdf" if name.lower().endswith(".pdf") else "text/plain"
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Indexing..."):
                ok, resp = post_file("/v1/upload", name, data, mime)
            if ok:
                st.success("Indexed ✅")
                st.json(resp)
            else:
                st.error("Upload failed")
                st.json(resp)

elif page == "Enter URL":
    st.subheader("🔗 (Optional) URL ingestion")
    st.info("URL ingestion endpoint is not implemented in this minimal build. (You can add /v1/url later.)")

elif page == "Ask Question":
    st.subheader("💬 Ask about your documents")
    q = st.text_input("Your question")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        top_k = st.slider("Passages", 4, 20, 8, 1)
    with c2:
        mode = st.radio("Mode", ["semantic", "hybrid"], horizontal=True)
    with c3:
        alpha = st.slider("Blend α (0=BM25,1=semantic)", 0.0, 1.0, 0.6, 0.1)

    col = st.columns([1,1,2])
    if st.button("Answer (with sources)", type="primary", disabled=not q):
        with st.spinner("Thinking..."):
            ok, resp = post_json("/v1/answer", {"question": q, "top_k": top_k, "mode": mode, "alpha": alpha})
        if ok:
            st.success(resp.get("answer", ""))
            srcs = resp.get("sources", [])
            if srcs:
                with st.expander("Sources"):
                    for s in srcs:
                        lbl = f"{s.get('source','?')} p.{s.get('page','?')}"
                        st.markdown(f"- **{lbl}** — {s.get('preview','')}")
        else:
            st.error("Answer failed")
            st.json(resp)

elif page == "Quiz Mode":
    st.subheader("📝 Quiz Mode")
    topic = st.text_input("Topic (optional)", placeholder="e.g., hybrid search")
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        n = st.slider("Questions", 3, 20, 5, 1)
    with c2:
        difficulty = st.radio("Difficulty", ["easy", "med", "hard"], horizontal=True)
    with c3:
        alpha = st.slider("Blend α", 0.0, 1.0, 0.6, 0.1)
    mode = st.radio("Mode", ["hybrid", "semantic"], horizontal=True)
    if st.button("Generate Quiz", type="primary"):
        with st.spinner("Generating..."):
            ok, resp = post_json("/v1/quiz", {"topic": topic or None, "n": n, "difficulty": difficulty, "mode": mode, "alpha": alpha})
        if ok:
            for i, qa in enumerate(resp.get("items", []), start=1):
                with st.expander(f"Q{i}. {qa['question']}"):
                    st.markdown(f"**Answer:** {qa['answer']}")
                    src = qa.get("source"); page = qa.get("page")
                    if src:
                        st.caption(f"Source: {src} p.{page}")
        else:
            st.error("Quiz failed")
            st.json(resp)

elif page == "Documents":
    st.subheader("📚 Indexed Documents")
    try:
        r = requests.get(f"{BACKEND_URL}/v1/documents", timeout=TIMEOUT_SECS)
        r.raise_for_status()
        data = r.json()
        st.json(data)
    except Exception as e:
        st.error(str(e))
