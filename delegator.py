# delegator.py
from agents import SubjectAgent

def assign_agent(category: str):
    name = category.lower()
    return SubjectAgent(name)
