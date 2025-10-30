# app/app_ui.py

from __future__ import annotations

import os
import json
from typing import Any, Dict, Tuple

import requests
import streamlit as st

# ────────────────────────────────────────────────────────────────────────────────
# App config
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduRAG – Learn from your documents",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Single source of truth for backend URL + timeouts
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT_SECS = int(os.getenv("BACKEND_TIMEOUT", "15"))

# ────────────────────────────────────────────────────────────────────────────────
# Tiny helpers
# ────────────────────────────────────────────────────────────────────────────────
def _pretty_error(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"status_code": resp.status_code, "text": resp.text}


@st.cache_data(ttl=5)
def healthz() -> bool:
    try:
        r = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
        r.raise_for_status()
        data = r.json()
        return bool(data.get("ok", False))
    except Exception:
        return False


def post_json(path: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    url = f"{BACKEND_URL}{path}"
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT_SECS)
        r.raise_for_status()
        return True, r.json()
    except requests.HTTPError:
        return False, _pretty_error(r)
    except Exception as e:
        return False, {"detail": str(e)}


def get_json(path: str) -> Tuple[bool, Dict[str, Any]]:
    url = f"{BACKEND_URL}{path}"
    try:
        r = requests.get(url, timeout=TIMEOUT_SECS)
        r.raise_for_status()
        return True, r.json()
    except requests.HTTPError:
        return False, _pretty_error(r)
    except Exception as e:
        return False, {"detail": str(e)}


def post_file(path: str, file_name: str, data: bytes, mime: str) -> Tuple[bool, Dict[str, Any]]:
    url = f"{BACKEND_URL}{path}"
    files = {"file": (file_name, data, mime)}
    try:
        r = requests.post(url, files=files, timeout=TIMEOUT_SECS)
        r.raise_for_status()
        return True, r.json()
    except requests.HTTPError:
        return False, _pretty_error(r)
    except Exception as e:
        return False, {"detail": str(e)}


# ────────────────────────────────────────────────────────────────────────────────
# Styles
# ────────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      .app-title { font-size: 2.2rem; font-weight: 800; letter-spacing: 0.2px; }
      .muted    { color: rgba(255,255,255,.6); }
      .pill     { padding: .55rem .8rem; border-radius: .6rem; font-weight: 600; }
      .pill-ok  { background: #123d29; border: 1px solid #1f7a55; }
      .pill-bad { background: #3b0f12; border: 1px solid #a03e46; }
      .card     { background: #1e1f25; padding: 1rem 1.2rem; border-radius: .8rem; border: 1px solid #2b2d36; }
      .section  { margin-top: .6rem; }
      .btn-wide button { width: 100% !important; }
      .footnote { font-size: .85rem; opacity: .7; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Main Menu")

    page = st.radio(
        label="Navigation",
        options=["Upload Document", "Enter URL", "Ask Question", "Quiz Mode", "Documents"],
        index=0,
    )

    st.caption(f"Backend: {BACKEND_URL}")

# ────────────────────────────────────────────────────────────────────────────────
# Header + health
# ────────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">EduRAG — Learn from your documents</div>', unsafe_allow_html=True)

healthy = healthz()
if healthy:
    st.markdown('<div class="pill pill-ok">✅ Backend OK</div>', unsafe_allow_html=True)
else:
    st.markdown(
        f'<div class="pill pill-bad">🚫 Backend unreachable at <b>{BACKEND_URL}</b></div>',
        unsafe_allow_html=True,
    )
    st.stop()

st.divider()

# ────────────────────────────────────────────────────────────────────────────────
# Pages
# ────────────────────────────────────────────────────────────────────────────────
if page == "Upload Document":
    st.subheader("📤 Upload your document (PDF/TXT)")

    uploaded = st.file_uploader(
        "Drag & drop or browse:",
        type=["pdf", "txt"],
        accept_multiple_files=False,
        help="Limit 200MB per file • PDF, TXT",
    )

    if uploaded:
        file_name = uploaded.name
        data = uploaded.getvalue()
        ext = file_name.lower().split(".")[-1]
        mime = "application/pdf" if ext == "pdf" else "text/plain"

        st.write(f"📄 **{file_name}**  ·  *{len(data)/1024:.1f} KB*")

        col_l, col_r = st.columns([1, 2])
        with col_l:
            do_upload = st.button("Upload & Index", type="primary")
        with col_r:
            st.caption("This sends the file to `/v1/upload` and triggers indexing.")

        if do_upload:
            with st.spinner("Uploading to backend…"):
                ok, resp = post_file("/v1/upload", file_name, data, mime)
            if ok:
                st.success("Indexed ✅")
                st.json(resp)
            else:
                st.error("Upload failed.")
                st.json(resp)

elif page == "Enter URL":
    st.subheader("🔗 Add a web page by URL")
    url = st.text_input("URL to ingest", placeholder="https://example.com/article")
    col_l, col_r = st.columns([1, 2])
    with col_l:
        run = st.button("Fetch & Index", type="primary", disabled=not url)
    with col_r:
        st.caption("Calls `/v1/url` to fetch & chunk the page content.")

    if run and url:
        with st.spinner("Fetching & indexing URL…"):
            ok, resp = post_json("/v1/url", {"url": url})
        if ok:
            st.success("URL ingested!")
            st.json(resp)
        else:
            st.error("Failed to ingest the URL.")
            st.json(resp)

elif page == "Ask Question":
    st.subheader("💬 Ask a question about your uploaded documents")

    q = st.text_input("Your question", placeholder="e.g., What is the main idea of chapter 3?")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        top_k = st.slider("How many passages", min_value=4, max_value=20, value=8, step=1)
    with c2:
        mode = st.radio("Search mode", options=["semantic", "hybrid"], horizontal=True, index=1)

    col_l, col_r = st.columns([1, 2])
    with col_l:
        btn_answer = st.button("Answer (with citations)", type="primary", disabled=not q)
    with col_r:
        st.caption("First tries `/v1/answer`; if not available, falls back to `/v1/query`.")

    if btn_answer and q:
        payload = {"question": q, "top_k": top_k, "mode": mode}
        with st.spinner("Thinking…"):
            ok, resp = post_json("/v1/answer", payload)

        if ok:
            st.success("Answer")
            st.write(resp.get("answer", ""))
            if "sources" in resp:
                with st.expander("Sources"):
                    st.json(resp["sources"])
        else:
            with st.spinner("No `/v1/answer`; showing top passages from `/v1/query`…"):
                ok2, resp2 = post_json("/v1/query", {"query": q, "top_k": top_k, "mode": mode})
            if ok2:
                st.info("Top passages (fallback)")
                st.json(resp2)
            else:
                st.error("The backend didn't return results.")
                st.json(resp)

elif page == "Quiz Mode":
    st.subheader("🧠 Quiz Mode (auto-generate from your docs)")

    topic = st.text_input("Topic (optional)", placeholder="e.g., hybrid search")
    q_count = st.slider("Questions", 3, 20, 5)
    diff = st.radio("Difficulty", ["easy", "med", "hard"], horizontal=True, index=0)
    quiz_mode = st.radio("Mode", ["hybrid", "semantic"], horizontal=True, index=0)

    if st.button("Generate Quiz", type="primary"):
        payload = {
            "topic": topic or None,
            "n": q_count,
            "difficulty": diff,
            "mode": quiz_mode,
        }
        with st.spinner("Generating quiz…"):
            ok, resp = post_json("/v1/quiz", payload)
        if ok:
            st.success("Quiz ready!")
            st.json(resp)
        else:
            st.error("Quiz failed")
            st.json(resp)

elif page == "Documents":
    st.subheader("📚 Documents indexed")
    ok, resp = get_json("/v1/docs")
    if ok:
        st.json(resp)
    else:
        st.info("Docs endpoint unavailable or empty.")
        st.json(resp)

# ────────────────────────────────────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <br>
    <div class="muted">
      <span class="footnote">Developed by <b>Your Name</b> · EduRAG Project</span>
    </div>
    """,
    unsafe_allow_html=True,
)
