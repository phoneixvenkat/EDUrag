from transformers import pipeline

# light summarizer; downloads on first use
_summarizer = pipeline("summarization", model="facebook/bart-base")

def summarize_text(text: str) -> str:
    text = (text or "")[:4000]
    if not text.strip():
        return "No content to summarize."
    out = _summarizer(text, max_length=180, min_length=60, do_sample=False)
    return out[0]["summary_text"]

def generate_answer(question: str, context: str) -> str:
    prompt = f"Answer the question concisely based on the context.\n\nQuestion: {question}\n\nContext: {context}\n\nAnswer:"
    out = _summarizer(prompt[:4000], max_length=160, min_length=40, do_sample=False)
    return out[0]["summary_text"]
