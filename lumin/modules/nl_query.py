import os
import re
import ast as pyast
import streamlit as st
from groq import Groq
import pandas as pd
import numpy as np
from prompts.templates import nl_to_code_prompt, nl_to_sql_prompt

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


def ask_groq(prompt: str, system: str = "You are an expert data analyst.") -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Groq API Error: {str(e)}")
        return ""


def clean_code(raw_response: str) -> str:
    """Strip fences and pure visualization lines. Never touch data computation lines."""
    code = raw_response.strip()

    # Strip markdown fences
    for fence in ("```python", "```"):
        if code.startswith(fence):
            code = code[len(fence):]
            break
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()

    # Drop pure visualization lines
    VIZ_PREFIXES = (
        "plt.", "ax.", "sns.",
        "import matplotlib", "from matplotlib",
        "import seaborn", "from seaborn",
        "fig, ax", "fig =", "fig=",
        "_, ax", "axes =",
    )
    lines = code.splitlines()
    data_lines = [l for l in lines if not any(l.strip().startswith(p) for p in VIZ_PREFIXES)]
    code = "\n".join(data_lines).strip()

    # Strip trailing .plot(...) using balanced paren counter
    def strip_trailing_plot(line: str) -> str:
        idx = line.find(".plot(")
        if idx == -1:
            return line
        depth = 0
        for i, ch in enumerate(line[idx:]):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = idx + i + 1
                    remainder = line[end:].strip()
                    if remainder == "" or remainder.startswith("#"):
                        return line[:idx].rstrip()
                    return line
        return line

    code = "\n".join(strip_trailing_plot(l) for l in code.splitlines()).strip()
    return code


def split_setup_and_result(code: str):
    """
    Split multi-line code into:
    - setup_code: lines that are assignments / mutations (no result value)
    - result_expr: the final expression that produces a value

    Example:
        df['Date'] = pd.to_datetime(df['Date'])   <- setup
        df.groupby('Date')['Sales'].sum()          <- result_expr
    """
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return "", ""

    # If only one line, it's the result expression
    if len(lines) == 1:
        return "", lines[0]

    # Check if last line is a pure expression (not an assignment)
    last = lines[-1].strip()
    try:
        tree = pyast.parse(last, mode='eval')
        # It parsed as an expression — it's our result
        return "\n".join(lines[:-1]), last
    except SyntaxError:
        # Last line is a statement (assignment etc) — no clear result expr
        return "\n".join(lines), ""


FORBIDDEN_PATTERNS = [
    "os.system", "subprocess", "open(", "__import__",
    "eval(", "exec(", "shutil", "socket", "requests",
    "urllib", "builtins", "globals()", "locals()",
]

SAFE_IMPORTS = {
    "import pandas as pd",
    "import numpy as np",
    "import re",
    "import matplotlib",
    "import matplotlib.pyplot as plt",
    "from matplotlib import pyplot as plt",
    "from collections import Counter",
    "from datetime import datetime",
    "import plotly.express as px",
    "import plotly.graph_objects as go",
}


def is_safe_code(code: str) -> bool:
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in code:
            return False
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            if s not in SAFE_IMPORTS:
                return False
    return True


def _is_bad_result(result) -> bool:
    import types
    return isinstance(result, types.ModuleType) or result is None



def generate_sql_equivalent(question: str, schema: str, sample: str) -> str:
    """Generate the SQL equivalent of a natural language question. Non-blocking — returns empty string on failure."""
    try:
        prompt = nl_to_sql_prompt(question, schema, sample)
        raw = ask_groq(prompt)
        # Strip fences
        sql = raw.strip()
        for fence in ("```sql", "```"):
            if sql.startswith(fence):
                sql = sql[len(fence):]
        if sql.endswith("```"):
            sql = sql[:-3]
        return sql.strip()
    except:
        return ""

def execute_nl_query(question: str, df: pd.DataFrame, schema: str, sample: str, extra_dfs: dict = None):
    prompt = nl_to_code_prompt(question, schema, sample)

    with st.spinner("Thinking..."):
        raw_code = ask_groq(prompt)

    code = clean_code(raw_code)

    # Retry if LLM returned garbage
    if not code or code.strip() in ("pd", "np", "df"):
        retry_prompt = (
            f"Write a single Python/Pandas expression using 'df' that answers: '{question}'\n"
            f"Schema: {schema}\n"
            f"Return ONLY the code. No explanation. No markdown.\n"
            f"The result MUST be a DataFrame or Series.\n"
            f"Example: df.groupby('Date')['Sales'].sum().reset_index()"
        )
        with st.spinner("Retrying..."):
            raw_code = ask_groq(retry_prompt)
        code = clean_code(raw_code)

    if not code:
        return None, "Couldn't generate code for that question. Try rephrasing it."

    if not is_safe_code(code):
        return None, "Couldn't visualize that — the generated code was blocked for safety."

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Work on a copy so date parsing mutations don't affect the real df
    allowed_globals = {
        "df": df.copy(),
        "pd": pd, "np": np, "plt": plt
    }
    if extra_dfs:
        allowed_globals.update(extra_dfs)

    local_vars = {}

    try:
        # KEY FIX: split setup lines from result expression
        # e.g. df['Date'] = pd.to_datetime(...) is setup
        #      df.groupby('Date')['Sales'].sum() is the result
        setup, result_expr = split_setup_and_result(code)

        # Run setup lines first (mutations, date parsing, etc.)
        if setup:
            exec(setup, allowed_globals, local_vars)
            # Merge local_vars back so result_expr can see them
            allowed_globals.update(local_vars)

        # Evaluate the result expression
        if result_expr:
            result = eval(result_expr, allowed_globals, local_vars)
        elif "result" in local_vars:
            result = local_vars["result"]
        elif local_vars:
            result = list(local_vars.values())[-1]
        else:
            result = None

        # Catch Axes/Figure objects from any remaining .plot() calls
        result_type = type(result).__name__
        if result_type in ("Axes", "AxesSubplot", "Figure"):
            # The result expression was a .plot() call — re-eval without it
            clean_expr = re.sub(r'\.plot\s*\(.*\)$', '', result_expr).strip()
            if clean_expr:
                result = eval(clean_expr, allowed_globals, local_vars)
            else:
                return None, "Couldn't visualize that — try asking for the data directly instead of requesting a plot."

        if _is_bad_result(result):
            return None, "Couldn't visualize that question. Try rephrasing it — be more specific about which columns you want."

        return result, code

    except Exception as e:
        return None, f"Couldn't visualize that question. Try rephrasing it.\n\n**Details:** {str(e)}"