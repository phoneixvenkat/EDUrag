from __future__ import annotations
from typing import List, Dict, Any
import random, re

WORD = re.compile(r"[A-Za-z][A-Za-z\-]{3,}")  # simple 'keyword' heuristic

def _pick_target(text: str) -> str | None:
    # choose a candidate keyword to blank out
    words = [w for w in WORD.findall(text or "") if w[0].isalpha()]
    if not words:
        return None
    # prefer capitalized or longer words
    words.sort(key=lambda w: (w[0].isupper(), len(w)), reverse=True)
    return words[0]

def _make_mcq_from_chunk(snippet: str, page: int | None, distractor_pool: List[str]) -> Dict[str, Any] | None:
    target = _pick_target(snippet)
    if not target or target.lower() not in snippet.lower():
        return None
    stem = re.sub(re.compile(re.escape(target), re.IGNORECASE), "_____", snippet, count=1)
    # build options
    distractors = [d for d in distractor_pool if d.lower() != target.lower()]
    random.shuffle(distractors)
    options = [target] + distractors[:3]
    random.shuffle(options)
    answer_idx = options.index(target)
    return {
        "question": f"Fill the blank: {stem[:220]}",
        "options": options,
        "answer_index": answer_idx,
        "page": page,
    }

def generate_quiz_from_chunks(chunks: List[Dict[str, Any]], k: int = 3) -> List[Dict[str, Any]]:
    # Build a global pool of candidate words for distractors
    pool = []
    for c in chunks:
        pool += [w for w in WORD.findall(c.get("snippet") or "") if len(w) > 3]
    pool = list({w for w in pool})  # dedupe
    random.shuffle(pool)

    # try to create k items from top chunks
    quiz: List[Dict[str, Any]] = []
    for c in chunks:
        it = _make_mcq_from_chunk(c.get("snippet") or "", c.get("page"), pool)
        if it:
            quiz.append(it)
        if len(quiz) >= k:
            break
    return quiz
