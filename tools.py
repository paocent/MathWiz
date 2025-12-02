# tools.py
from crewai.tools import tool
from rag_engine import retrieve
from calculator import solve_math_expression
from llm_clients import generate
import json

# -------------------------------------------------------------------
# INTERNAL CHAIN OF THOUGHT LOGGER (never sent to user)
# -------------------------------------------------------------------
CHAIN_OF_THOUGHT_LOG = []

def log_thought(step: str, data: dict):
    """Log internal reasoning steps for debugging purposes."""
    CHAIN_OF_THOUGHT_LOG.append({"step": step, "data": data})

def get_chain_of_thought(clear: bool = True):
    """Return internal chain of thought log. Optionally clears it."""
    global CHAIN_OF_THOUGHT_LOG
    log_copy = CHAIN_OF_THOUGHT_LOG.copy()
    if clear:
        CHAIN_OF_THOUGHT_LOG.clear()
    return log_copy

# -------------------------------------------------------------------
# 1) PRIMARY GENERAL MATH SOLVER (internal Python function)
# -------------------------------------------------------------------
def general_math_solver(question: str) -> dict:
    """Internal Python solver for general math questions."""
    try:
        result = solve_math_expression(question)
        confidence = 0.95
        log_thought("general_solver", {"question": question, "result": result})
        return {"success": True, "result": result, "confidence": confidence}
    except Exception as e:
        return {"success": False, "result": None, "confidence": 0.0, "error": str(e)}

# CrewAI Tool wrapper
@tool("General Math Solver Tool")
def general_math_solver_tool(question: str) -> str:
    """CrewAI tool: solves a general math question and returns JSON string."""
    res = general_math_solver(question)
    return json.dumps(res)

# -------------------------------------------------------------------
# 2) RAG PDF SOLVER
# -------------------------------------------------------------------
def rag_solver(question: str, top_k: int = 4) -> dict:
    """Internal function to query PDF knowledge base."""
    results = retrieve(question, top_k=top_k)
    log_thought("rag", {"question": question, "results_count": len(results)})
    return {"success": True, "chunks": results}

@tool("RAG PDF Math Solver")
def rag_tool_query(question: str, top_k: int = 4) -> str:
    """CrewAI tool: retrieves relevant PDF chunks for the question."""
    res = rag_solver(question, top_k=top_k)
    return json.dumps(res)

# -------------------------------------------------------------------
# 3) LLM FALLBACK
# -------------------------------------------------------------------
def llm_fallback(question: str) -> dict:
    """Internal function: uses LLM to solve math question."""
    answer = generate(f"Solve the following math problem: {question}")
    log_thought("fallback_llm", {"question": question, "answer": answer})
    return {"success": True, "answer": answer}

@tool("LLM Fallback Reasoner")
def llm_fallback_tool(question: str) -> str:
    """CrewAI tool: generates an answer using LLM fallback."""
    res = llm_fallback(question)
    return json.dumps(res)

# -------------------------------------------------------------------
# 4) LLM lightweight wrapper
# -------------------------------------------------------------------
def llm_text(prompt: str) -> str:
    """Return plain text output from LLM."""
    res = generate(prompt)
    if res.get("success"):
        return res.get("text", "")
    return f"[LLM Error] {res.get('error')}"
