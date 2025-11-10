# eval_models.py
"""
Run RAG evaluations across multiple open-source LLMs using the SAME retrieved context.

Workflow:
1) For each question -> call your backend /v1/query to get top-k passages.
2) For each model in configs/models.json -> call the model (OpenAI-compatible API) with a fixed prompt.
3) Save all outputs + basic stats to results/eval_<timestamp>.json and CSV.

Requirements: requests, python-dotenv, openai, pandas (add to requirements.txt if missing).
"""

from __future__ import annotations
import os, json, time, csv, pathlib
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

# ------------------------ Config ------------------------
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
TOP_K       = int(os.getenv("EVAL_TOP_K", "8"))
MODE        = os.getenv("EVAL_MODE", "hybrid")  # "semantic" or "hybrid"
QUESTIONS   = os.getenv("EVAL_QUESTIONS_FILE", "questions.txt")
MODELS_FILE = os.getenv("EVAL_MODELS_FILE",   "configs/models.json")

RESULTS_DIR = pathlib.Path("results"); RESULTS_DIR.mkdir(exist_ok=True, parents=True)

SYSTEM_INSTRUCTION = (
    "You are a careful assistant. Use ONLY the provided context to answer. "
    "If the context is insufficient, say so. Cite spans using [1],[2],… where relevant. "
    "Keep temperature low for determinism."
)

USER_PROMPT_TEMPLATE = """Question: {question}

Context:
{context}

Instructions:
- Answer concisely (5-8 sentences).
- Cite using [1],[2],… to indicate which passage you used.
"""

# ------------------------ Helpers ------------------------
def load_models(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def load_questions(path: str) -> List[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Questions file not found: {path}")
    qs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                qs.append(line)
    return qs

def backend_query(question: str, top_k: int, mode: str) -> List[str]:
    """Call your /v1/query endpoint; return a list of passage strings."""
    url = f"{BACKEND_URL}/v1/query"
    payload = {"query": question, "top_k": top_k, "mode": mode}
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    passages = [p["text"] for p in data.get("chunks", [])]
    return passages

def call_llm(model_cfg: Dict[str, Any], question: str, passages: List[str]) -> Dict[str, Any]:
    base_url = model_cfg.get("base_url")
    api_key  = model_cfg.get("api_key")
    model    = model_cfg.get("model")
    name     = model_cfg.get("name", model)

    client = OpenAI(base_url=base_url, api_key=api_key)
    context = "\n\n".join([f"[{i+1}] {p}" for i, p in enumerate(passages)])

    prompt = USER_PROMPT_TEMPLATE.format(question=question, context=context)
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt},
        ],
    )
    dt = time.time() - t0
    content = resp.choices[0].message.content.strip() if resp.choices else ""
    tokens_out = getattr(resp.usage, "completion_tokens", None) if hasattr(resp, "usage") else None
    tokens_in  = getattr(resp.usage, "prompt_tokens", None)     if hasattr(resp, "usage") else None

    return {
        "provider_name": name,
        "model": model,
        "latency_sec": round(dt, 3),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "answer": content,
    }

# ------------------------ Main ------------------------
def main():
    models = load_models(MODELS_FILE)
    questions = load_questions(QUESTIONS)

    rows_csv = []
    all_json = {
        "backend_url": BACKEND_URL,
        "top_k": TOP_K,
        "mode": MODE,
        "questions_file": QUESTIONS,
        "models": [m["name"] for m in models],
        "results": []
    }

    for q_idx, q in enumerate(questions, 1):
        passages = backend_query(q, top_k=TOP_K, mode=MODE)
        if not passages:
            print(f"[WARN] No passages for Q{q_idx}: {q}")
            continue

        for m in models:
            try:
                out = call_llm(m, q, passages)
            except Exception as e:
                out = {"provider_name": m.get("name"), "model": m.get("model"), "error": str(e), "answer": ""}

            row = {
                "q_idx": q_idx,
                "question": q,
                "provider_name": out.get("provider_name"),
                "model": out.get("model"),
                "latency_sec": out.get("latency_sec"),
                "tokens_in": out.get("tokens_in"),
                "tokens_out": out.get("tokens_out"),
                "answer": out.get("answer", ""),
            }
            rows_csv.append(row)
            all_json["results"].append(row)
            print(f"[OK] Q{q_idx} · {row['provider_name']} · {row['model']} · {row['latency_sec']}s")

    # Save results as JSON & CSV
    ts = time.strftime("%Y%m%d_%H%M%S")
    json_path = pathlib.Path("results") / f"eval_{ts}.json"
    csv_path  = pathlib.Path("results") / f"eval_{ts}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_json, f, ensure_ascii=False, indent=2)

    pd.DataFrame(rows_csv).to_csv(csv_path, index=False)
    print(f"\nSaved:\n- {json_path}\n- {csv_path}\n")

if __name__ == "__main__":
    main()
