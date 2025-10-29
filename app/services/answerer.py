from sentence_transformers import CrossEncoder

# small local reranker/summarizer
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def generate_answer(query, passages):
    pairs = [[query, p] for p in passages]
    scores = model.predict(pairs)
    ranked = [p for _, p in sorted(zip(scores, passages), reverse=True)]
    top = " ".join(ranked[:3])
    return f"Answer summary: {top[:500]}..."
