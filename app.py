# app.py
import streamlit as st
from main import answer_question
from tools import get_chain_of_thought  # Use getter instead of direct list
import json

st.set_page_config(page_title="Math Wiz MK. II", layout="wide")

st.title("🧮 Math Wiz MK. II - Agentic Math Solver")
st.write(
    "Ask any math question. Algebra, Calculus, Statistics, or General Math. "
    "RAG fallback and LLM fallback enabled."
)

# --- User input ---
user = st.text_input("Enter your name:", value="anonymous")

# --- Example prompts table ---
st.markdown("### 📚 Example Prompts")
st.markdown(
    """
    | Algebra | Calculus | Statistics | General Math |
    |---------|----------|------------|--------------|
    | Solve for x: 2x + 5 = 15 | Derivative of x^2 + 3x | Mean of [2,4,6,8] | 12 × 8 |
    | Factorize x^2 + 5x + 6 | ∫(3x^2) dx | Standard deviation of [1,2,3,4] | √144 |
    | Simplify 3(x - 2) + 4x | Limit as x→0 of sin(x)/x | Probability of heads in a fair coin | 15% of 200 |
    | Solve 3x/2 = 9 | d/dx (e^x) | Median of [3,1,4,2,5] | 45 ÷ 5 |
    | If 2x - 3 = 7, what is x? | Find f'(x) if f(x) = ln(x) | Variance of [2,4,4,4,5,5,7] | Solve 3 + 7 × 2 |
    """,
    unsafe_allow_html=True
)

# --- Text area for custom question ---
question = st.text_area("Enter your math question:")

# --- Solve Question ---
if st.button("Solve Question"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            res = answer_question(question, user=user)

        # --- Nicely formatted answer ---
        st.markdown("### ✅ Answer")
        st.markdown(
            f"""
            <div style='background-color:#000000;color:#ffffff;padding:15px;border-radius:10px;border:1px solid #333333'>
                <p style='font-size:18px;'>{res.get("answer")}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Readable Text for user ---
        st.markdown("### 📝 Readable Text")
        readable_text = res.get("answer")

        # Handle dict or nested LLM response
        if isinstance(readable_text, dict):
            if 'text' in readable_text:
                readable_text = readable_text['text']
            else:
                # Try to pretty print JSON if available
                try:
                    readable_text = json.dumps(readable_text, indent=2)
                except Exception:
                    readable_text = str(readable_text)

        # Display in a nice box
        st.markdown(
            f"""
            <div style='background-color:#1e1e1e;color:#ffffff;padding:15px;border-radius:10px;border:1px solid #333333'>
                <pre style='font-size:16px;'>{readable_text}</pre>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Display metadata ---
        st.markdown(f"**Method Used:** `{res.get('method')}`")
        st.markdown(f"**Category:** `{res.get('category')}`")
        st.markdown(f"**Confidence:** `{res.get('confidence'):.2f}`")

        # --- Feedback / Reflection ---
        st.markdown("### 📝 Feedback / Reflection")
        rating = st.slider("Rate how helpful the answer was:", min_value=0, max_value=5, value=3)
        feedback_text = st.text_area("Additional feedback or comments:")

        if st.button("Submit Feedback"):
            # Placeholder: save feedback to a database or file
            st.success("Thank you for your feedback!")
            st.write(f"Your rating: {rating}/5")
            st.write(f"Your comments: {feedback_text}")

        # --- Sidebar Chain-of-Thought ---
        st.sidebar.header("🧠 Chain of Thought (Internal Logs)")
        cot_log = get_chain_of_thought(clear=True)

        if cot_log:
            for i, step in enumerate(cot_log, 1):
                st.sidebar.markdown(f"**Step {i}: {step['step']}**")
                # Try to pretty print dicts for readability
                if isinstance(step['data'], dict):
                    data_str = json.dumps(step['data'], indent=2)
                else:
                    data_str = str(step['data'])
                st.sidebar.text(data_str)
        else:
            st.sidebar.info("No reasoning logged yet.")
