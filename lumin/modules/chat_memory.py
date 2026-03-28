import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from modules.nl_query import clean_code, is_safe_code, client
from modules.data_loader import get_schema, get_sample
from modules.visualizer import render_chart


def extract_code_from_reply(reply: str):
    """
    Robustly extract ONLY the executable code from LLM reply.
    Handles 3 cases:
    1. Pure code (no explanation)
    2. Explanation + ```python ... ``` fenced block  
    3. Mixed text with df. references scattered in explanation
    Returns (code_str, is_pure_text) 
    """
    # Case 1: Explicit fenced code block — extract just that
    fenced = re.search(r"```python\s*\n(.*?)```", reply, re.DOTALL)
    if fenced:
        return fenced.group(1).strip(), False

    # Case 2: No fence but reply is pure code (starts with df. or result =)
    stripped = reply.strip()
    first_line = stripped.splitlines()[0] if stripped else ""
    if first_line.startswith("df.") or first_line.startswith("result =") or first_line.startswith("pd."):
        return stripped, False

    # Case 3: Mixed explanation + code — check if there's a code line buried in text
    # Only treat as code if there's an actual executable pandas assignment
    code_lines = []
    for line in reply.splitlines():
        l = line.strip()
        if (l.startswith("result =") or 
            (l.startswith("df.") and "=" not in l[:5]) or
            l.startswith("pd.")):
            code_lines.append(l)

    if code_lines:
        return "\n".join(code_lines), False

    # No executable code found — it's a plain text response
    return "", True


def render_chat_tab(df: pd.DataFrame, extra_dfs: dict = None):
    # ── Mode banner ───────────────────────────────────────────────────────────
    bcol, clearcol = st.columns([9, 1])
    with bcol:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;
                    padding:14px 18px;background:#161616;border:1px solid #262626;
                    border-left:3px solid #2DD4BF;border-radius:8px;">
            <div style="font-size:20px;">💬</div>
            <div>
                <div style="font-family:IBM Plex Mono,monospace;font-size:11px;font-weight:600;
                            letter-spacing:0.1em;text-transform:uppercase;color:#2DD4BF;">
                    Chat Analyst</div>
                <div style="font-family:IBM Plex Sans,sans-serif;font-size:12px;color:#737373;margin-top:2px;">
                    Have a conversation — ask follow-up questions, get explanations and reasoning</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with clearcol:
        st.write("")
        st.write("")
        if st.button("Clear", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Render all previous messages first
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "result" in msg:
                result = msg["result"]
                try:
                    render_chart(result, msg.get("question", "Contextual query"), override_type="Auto")
                except:
                    st.write(result)

    # Chat input always renders at the bottom of the viewport
    prompt = st.chat_input("Ask anything about your data...")
    if prompt:
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                schema = get_schema(df)
                sample = get_sample(df)

                extra_schema = ""
                if extra_dfs:
                    for name, edf in extra_dfs.items():
                        extra_schema += f"\nExtra DataFrame '{name}':\n{get_schema(edf)}\n"

                system_prompt = f"""You are an expert data analyst. You have two modes:

MODE A — DATA QUERY: If the question requires computation or data lookup, respond with ONLY a single executable Python/Pandas code block. Rules:
- Use 'df' as the dataframe variable
- Store the final answer in a variable called 'result'
- NO explanation, NO markdown, NO comments — pure code only
- NEVER use matplotlib, plt, or any plotting library
- NEVER mix explanation text with code

MODE B — EXPLANATION: If the question asks for explanation, opinion, or reasoning (e.g. "explain", "why", "what factors", "which regions should"), respond with plain English text only. No code.

Schema of df:
{schema}
{extra_schema}
Sample (first 5 rows of df):
{sample}

IMPORTANT: Never mix text and code in the same response. Choose one mode only."""

                messages = [{"role": "system", "content": system_prompt}]
                context_msgs = st.session_state["chat_history"][-12:]
                for m in context_msgs:
                    messages.append({"role": m["role"], "content": m["content"]})

                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=0.2,
                        max_tokens=1024,
                    )
                    reply = response.choices[0].message.content.strip()
                except Exception as e:
                    st.error(f"API Error: {e}")
                    return

                # Robustly extract code vs plain text
                code_str, is_plain_text = extract_code_from_reply(reply)

                if is_plain_text or not code_str:
                    # Pure explanation response
                    st.markdown(reply)
                    st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                else:
                    # Code path
                    code = clean_code(code_str)

                    if not code.strip():
                        # After cleaning, nothing left — just show the reply as text
                        st.markdown(reply)
                        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                        return

                    if not is_safe_code(code):
                        st.warning("Blocked unsafe code execution.")
                        st.session_state["chat_history"].append({"role": "assistant", "content": "Blocked unsafe code."})
                        return

                    allowed_globals = {"df": df, "pd": pd, "np": np, "plt": plt}
                    if extra_dfs:
                        allowed_globals.update(extra_dfs)

                    local_vars = {}
                    try:
                        if "\n" not in code and not code.startswith("result ="):
                            exec_code = f"result = {code}"
                        else:
                            exec_code = code

                        exec(exec_code, allowed_globals, local_vars)

                        result = local_vars.get("result", list(local_vars.values())[-1] if local_vars else None)

                        content_str = f"**Executed Code:**\n```python\n{code}\n```"
                        st.markdown(content_str)

                        if result is not None:
                            render_chart(result, prompt, override_type="Auto")
                        else:
                            st.info("Code executed successfully but returned no result.")

                        st.session_state["chat_history"].append({
                            "role": "assistant",
                            "content": content_str,
                            "result": result,
                            "question": prompt
                        })

                    except Exception as e:
                        err_msg = "Couldn't visualize that — try rephrasing your question or being more specific about the columns or chart type."
                        st.error(err_msg)
                        st.session_state["chat_history"].append({"role": "assistant", "content": err_msg})