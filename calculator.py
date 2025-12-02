# calculator.py
"""
Math expression solver used by the primary solver.
Attempts symbolic solve (SymPy), then numeric evaluation as fallback.
"""

import re

# Try to import SymPy if available (recommended)
try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except:
    SYMPY_AVAILABLE = False


def clean_expression(expr: str) -> str:
    """
    Removes unwanted characters to protect evaluation.
    Only digits, letters, math operators allowed.
    """
    allowed = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/().=^ "
    return "".join([c for c in expr if c in allowed])


def solve_math_expression(question: str) -> str:
    """
    Solves the math question.
    - If it's an equation: solve symbolically
    - If it's an expression: evaluate it
    Returns the final answer as a string.
    """

    expr = clean_expression(question)

    # -------------------------------------------------------------
    # CASE 1 — EQUATION (contains "=")
    # -------------------------------------------------------------
    if "=" in expr:
        if not SYMPY_AVAILABLE:
            raise Exception("SymPy not installed → unable to solve symbolic equations")

        left, right = expr.split("=")
        left = sp.sympify(left)
        right = sp.sympify(right)

        x = sp.symbols("x")

        solution = sp.solve(left - right, x)

        return f"x = {solution}"

    # -------------------------------------------------------------
    # CASE 2 — EXPRESSION (like 2+3, 5/6, 3^2 etc.)
    # -------------------------------------------------------------
    # Allow ^ exponent
    expr = expr.replace("^", "**")

    try:
        result = eval(expr, {"__builtins__": None}, {})
        return str(result)
    except Exception:
        pass

    # -------------------------------------------------------------
    # CASE 3 — SymPy evaluate if possible
    # -------------------------------------------------------------
    if SYMPY_AVAILABLE:
        try:
            result = sp.simplify(expr)
            return str(result)
        except:
            pass

    raise Exception(f"Unable to solve expression: {question}")
