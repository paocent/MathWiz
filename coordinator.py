# coordinator.py
def classify_question(question: str):
    q = question.lower()
    if any(k in q for k in ["solve", "x=", "=", "quadratic", "factor", "root"]):
        return {"category":"algebra", "confidence":0.9}
    if any(k in q for k in ["derivative", "integrate", "integral", "differentiate", "limit"]):
        return {"category":"calculus", "confidence":0.9}
    if any(k in q for k in ["mean", "median", "standard deviation", "variance", "probability"]):
        return {"category":"statistics", "confidence":0.9}
    return {"category":"general", "confidence":0.7}
