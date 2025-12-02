# reflection_agent.py
def evaluate_confidence(method: str, confidence: float):
    if method == "primary" and confidence >= 0.8:
        return "ok"
    if method == "rag" and confidence >= 0.4:
        return "ok"
    if method == "llm":
        return "review"
    return "needs_review"
