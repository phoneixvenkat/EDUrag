def extractive_answer(question: str, context: str) -> str:
    """
    Keep it deterministic & lightweight: return the best matching sentence window.
    (You can swap this for a real QA model later.)
    """
    if not context:
        return "No context available."
    # very naive: return first 500 chars of context as 'answer'
    return context[:500]
