# main.py
from coordinator import classify_question
from delegator import assign_agent

def answer_question(question: str, user: str = "anonymous") -> dict:
    """
    Main entry point for handling a math question.
    1. Classifies question category
    2. Assigns the correct agent
    3. Returns agent-handled answer
    """
    # 1) Classify question category
    cls = classify_question(question)
    category = cls.get("category", "general")

    # 2) Assign agent
    agent = assign_agent(category)

    # 3) Let agent handle the question
    result = agent.handle(question, convo_user=user)

    # 4) Return structured response
    return {
        "category": category,
        **result
    }
