def simple_answer(question: str, context: str) -> str:
    q_words = set(question.lower().split())
    sents = [s.strip() for s in context.split(".") if s.strip()]
    ranked = [s for s in sents if any(w in s.lower() for w in q_words)]
    if not ranked:
        ranked = sents[:3]
    return (". ".join(ranked[:4])).strip() or "No clear answer found in context."
