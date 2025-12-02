# agents.py
from tools import general_math_solver, rag_solver, llm_fallback, log_thought
from database import save_task_log, save_conversation, update_conversation_answer
from config import SOLVER_CONF_THRESH
import json


class SubjectAgent:
    """
    Represents a math agent (Algebra, Calculus, Statistics, General Math).
    Handles question solving with primary solver, RAG fallback, and LLM fallback.
    Logs detailed Chain-of-Thought for each stage.
    """

    def __init__(self, name: str):
        self.name = name

    def handle(self, question: str, convo_user: str = "anonymous") -> dict:
        """
        Handles a question end-to-end:
        1. Logs conversation
        2. Primary solver attempt
        3. RAG fallback if necessary
        4. LLM fallback if necessary
        5. Updates conversation & logs
        Returns a dict with final answer, method, and confidence
        """
        # ----------------------------------------------------
        # 0) Start conversation
        # ----------------------------------------------------
        convo_id = save_conversation(convo_user, question, None, "in-progress")
        final_answer = None
        method_used = "unknown"
        confidence_score = 0.0

        log_thought("step_0_start", {"question": question, "user": convo_user})
        log_thought("step_0_classification", {"predicted_category": self.name})

        # ----------------------------------------------------
        # 1) PRIMARY SOLVER
        # ----------------------------------------------------
        log_thought("step_1_primary_solver", {"status": "attempting"})
        primary = general_math_solver(question)
        save_task_log(convo_id, self.name, "primary_solver", "attempt", primary.get("confidence", 0.0), meta=primary)
        log_thought("step_1_primary_solver_result", primary)

        if primary.get("success") and primary.get("confidence", 0.0) >= SOLVER_CONF_THRESH:
            final_answer = primary.get("result")
            method_used = "primary_solver"
            confidence_score = primary.get("confidence", 0.0)
            update_conversation_answer(convo_id, json.dumps(final_answer), method_used)

            log_thought("step_1_primary_solver_final", {"answer": final_answer, "method": method_used, "confidence": confidence_score})
            return {"answer": final_answer, "method": method_used, "confidence": confidence_score}

        # ----------------------------------------------------
        # 2) RAG FALLBACK
        # ----------------------------------------------------
        log_thought("step_2_rag_solver", {"status": "attempting"})
        rag = rag_solver(question)
        save_task_log(convo_id, self.name, "rag_solver", "attempt", 0.0, meta=rag)

        rag_chunks = rag.get("chunks", [])
        log_thought("step_2_rag_solver_result", {"chunks_found": len(rag_chunks)})

        if rag_chunks:
            final_answer = " | ".join([c.get("text", "") for c in rag_chunks[:3]])
            method_used = "rag_solver"
            confidence_score = 0.85
            update_conversation_answer(convo_id, json.dumps(final_answer), method_used)

            log_thought("step_2_rag_solver_final", {"answer": final_answer, "method": method_used, "confidence": confidence_score})
            return {"answer": final_answer, "method": method_used, "confidence": confidence_score}

        # ----------------------------------------------------
        # 3) LLM FALLBACK
        # ----------------------------------------------------
        log_thought("step_3_llm_fallback", {"status": "attempting"})
        llm_res = llm_fallback(question)
        save_task_log(convo_id, self.name, "llm_fallback", "attempt", 0.0, meta=llm_res)
        log_thought("step_3_llm_fallback_result", {"raw_llm": str(llm_res)[:200]})  # preview only

        # Clean answer
        if isinstance(llm_res, dict):
            final_answer = llm_res.get("answer", "[LLM failed]")
        else:
            try:
                final_answer = json.loads(llm_res).get("answer", "[LLM failed]")
            except Exception:
                final_answer = "[LLM failed]"

        method_used = "llm_fallback"
        confidence_score = 0.7
        update_conversation_answer(convo_id, json.dumps(final_answer), method_used)

        log_thought("step_3_llm_fallback_final", {"answer": final_answer, "method": method_used, "confidence": confidence_score})

        # ----------------------------------------------------
        # 4) Return final answer
        # ----------------------------------------------------
        log_thought("step_4_end", {"final_answer": final_answer, "method": method_used, "confidence": confidence_score})
        return {"answer": final_answer, "method": method_used, "confidence": confidence_score}
