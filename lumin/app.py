import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI: Personalized Data Analyst",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from ui.styles import inject_css
from ui.components import render_topbar, render_data_strip, render_dashboard_tab, render_explorer_empty_state
from modules.data_loader import load_file, get_schema, get_sample, find_common_columns, merge_dataframes
from modules.nl_query import execute_nl_query, generate_sql_equivalent
from modules.visualizer import render_chart
from modules.insight_engine import generate_insight, generate_why_what_next
from modules.anomaly_detector import render_anomaly_detector_tab
from modules.what_if import render_what_if_tab
from modules.chat_memory import render_chat_tab
try:
    import pandasql as psql
    SQL_AVAILABLE = True
except ImportError:
    SQL_AVAILABLE = False


def render_landing():
    """Two-path landing page: single file vs multiple files."""
    st.markdown("""
    <div style="text-align:center;padding:64px 20px 40px;">
        <div style="font-family:Sora,sans-serif;font-size:11px;letter-spacing:0.18em;
                    text-transform:uppercase;color:#52525B;margin-bottom:18px;">Your data analyst awaits</div>
        <div style="font-family:Sora,sans-serif;font-size:42px;font-weight:700;
                    color:#F0F0F2;letter-spacing:-0.03em;line-height:1.15;margin-bottom:12px;">
            Turn your spreadsheet<br>into <span style="color:#F97316;">intelligence.</span>
        </div>
        <div style="font-family:Sora,sans-serif;font-size:15px;font-weight:300;
                    color:#71717A;max-width:440px;margin:0 auto 52px;line-height:1.7;">
            Choose how you want to explore — one focused dataset or multiple files working together.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_single, col_gap, col_multi = st.columns([5, 1, 5])

    # ── Single file path ──────────────────────────────────────────────────────
    with col_single:
        st.markdown("""
        <div style="border:1.5px solid #2A2A32;border-radius:16px;padding:28px 24px 20px;
                    background:#131316;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:38px;height:38px;background:rgba(249,115,22,0.15);
                            border:1px solid rgba(249,115,22,0.3);border-radius:10px;
                            display:flex;align-items:center;justify-content:center;font-size:18px;">📄</div>
                <div>
                    <div style="font-family:Sora,sans-serif;font-size:15px;font-weight:600;color:#F0F0F2;">
                        Single File</div>
                    <div style="font-family:Sora,sans-serif;font-size:12px;color:#52525B;margin-top:2px;">
                        Explore one CSV or Excel file</div>
                </div>
            </div>
            <div style="font-family:Sora,sans-serif;font-size:12px;color:#71717A;line-height:1.6;margin-bottom:16px;">
                ✓ Dashboard & data preview<br>
                ✓ AI-powered Q&A<br>
                ✓ Anomaly detection<br>
                ✓ What-If simulation
            </div>
        </div>
        """, unsafe_allow_html=True)

        single_file = st.file_uploader(
            "single", type=["csv", "xlsx", "xls"],
            accept_multiple_files=False,
            key="upload_single", label_visibility="collapsed"
        )
        if single_file:
            loaded = load_file(single_file)
            if loaded is not None:
                name = os.path.splitext(single_file.name)[0]
                st.session_state["all_dfs"] = {name: loaded}
                st.session_state["active_df"] = name
                st.session_state["mode"] = "single"
                st.session_state["chat_history"] = []
                st.session_state.pop("explorer_result", None)
                st.rerun()

    # ── Divider ───────────────────────────────────────────────────────────────
    with col_gap:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;
                    height:100%;padding-top:60px;">
            <div style="font-family:Sora,sans-serif;font-size:12px;color:#3A3A45;
                        writing-mode:vertical-rl;letter-spacing:0.1em;">OR</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Multiple files path ───────────────────────────────────────────────────
    with col_multi:
        st.markdown("""
        <div style="border:1.5px solid #2A2A32;border-radius:16px;padding:28px 24px 20px;
                    background:#131316;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:38px;height:38px;background:rgba(167,139,250,0.15);
                            border:1px solid rgba(167,139,250,0.3);border-radius:10px;
                            display:flex;align-items:center;justify-content:center;font-size:18px;">📂</div>
                <div>
                    <div style="font-family:Sora,sans-serif;font-size:15px;font-weight:600;color:#F0F0F2;">
                        Multiple Files</div>
                    <div style="font-family:Sora,sans-serif;font-size:12px;color:#52525B;margin-top:2px;">
                        Compare, join and cross-query datasets</div>
                </div>
            </div>
            <div style="font-family:Sora,sans-serif;font-size:12px;color:#71717A;line-height:1.6;margin-bottom:16px;">
                ✓ Individual dashboard per file<br>
                ✓ Join files on common columns<br>
                ✓ Cross-file AI queries<br>
                ✓ Compare datasets side by side
            </div>
        </div>
        """, unsafe_allow_html=True)

        multi_files = st.file_uploader(
            "multi", type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            key="upload_multi", label_visibility="collapsed"
        )
        if multi_files and len(multi_files) >= 1:
            dfs = {}
            for f in multi_files:
                loaded = load_file(f)
                if loaded is not None:
                    dfs[os.path.splitext(f.name)[0]] = loaded
            if dfs:
                st.session_state["all_dfs"] = dfs
                st.session_state["active_df"] = list(dfs.keys())[0]
                st.session_state["mode"] = "multi"
                st.session_state["chat_history"] = []
                st.session_state.pop("explorer_result", None)
                st.rerun()


def render_multi_file_header(all_dfs, active_name):
    """File switcher tabs for multi-file mode."""
    names = list(all_dfs.keys())

    st.markdown("""
    <div style="padding:12px 40px 0;background:#131316;border-bottom:1px solid #2A2A32;">
        <div style="font-family:Sora,sans-serif;font-size:10px;letter-spacing:0.12em;
                    text-transform:uppercase;color:#52525B;margin-bottom:10px;">Active Dataset</div>
    </div>
    """, unsafe_allow_html=True)

    header_cols = st.columns([4, 2, 2])
    with header_cols[0]:
        selected = st.selectbox(
            "dataset", names,
            index=names.index(active_name),
            key="active_df_select",
            label_visibility="collapsed"
        )
        if selected != active_name:
            st.session_state["active_df"] = selected
            st.session_state.pop("explorer_result", None)
            st.rerun()

    with header_cols[1]:
        # Quick stats inline
        df_active = all_dfs[selected]
        st.markdown(
            f'<div style="padding:8px 0;font-family:Sora,sans-serif;font-size:11px;color:#71717A;">'
            f'<span style="color:#F0F0F2;font-weight:600;">{df_active.shape[0]:,}</span> rows &nbsp;·&nbsp; '
            f'<span style="color:#F0F0F2;font-weight:600;">{df_active.shape[1]}</span> cols'
            f'</div>',
            unsafe_allow_html=True
        )

    with header_cols[2]:
        if st.button("＋ Add another file", key="add_file_btn"):
            st.session_state["show_add_file"] = True

    if st.session_state.get("show_add_file"):
        new_file = st.file_uploader(
            "Add file", type=["csv","xlsx","xls"],
            key="add_file_uploader", label_visibility="collapsed"
        )
        if new_file:
            loaded = load_file(new_file)
            if loaded is not None:
                name = os.path.splitext(new_file.name)[0]
                all_dfs[name] = loaded
                st.session_state["all_dfs"] = all_dfs
                st.session_state["active_df"] = name
                st.session_state["show_add_file"] = False
                st.rerun()

    return selected


def main():
    inject_css()

    api_key = os.environ.get("GROQ_API_KEY", "")
    api_ok  = bool(api_key and api_key != "gsk_placeholder")
    all_dfs = st.session_state.get("all_dfs", {})

    render_topbar(api_ok)

    # ── Landing page ──────────────────────────────────────────────────────────
    if not all_dfs:
        render_landing()
        return

    # ── Determine active df ───────────────────────────────────────────────────
    active_options = list(all_dfs.keys())
    active_name = st.session_state.get("active_df", active_options[0])
    if active_name not in active_options:
        active_name = active_options[0]

    mode = st.session_state.get("mode", "single")

    # ── Multi-file header ─────────────────────────────────────────────────────
    if mode == "multi" or len(all_dfs) > 1:
        active_name = render_multi_file_header(all_dfs, active_name)

    df = all_dfs[active_name]
    extra_dfs = {k: v for k, v in all_dfs.items() if k != active_name}
    schema = get_schema(df)
    sample = get_sample(df)

    # ── Stat strip ────────────────────────────────────────────────────────────
    render_data_strip(df)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Join UI for multi-file ────────────────────────────────────────────────
    if len(all_dfs) >= 2:
        with st.expander("Join datasets", expanded=False):
            df_names = list(all_dfs.keys())
            jc1, jc2, jc3, jc4 = st.columns([2,2,2,1])
            with jc1: left     = st.selectbox("Left table", df_names, key="join_left")
            with jc2: right    = st.selectbox("Right table", [n for n in df_names if n != left], key="join_right")
            with jc3:
                common   = list(set(all_dfs[left].columns) & set(all_dfs[right].columns))
                join_col = st.selectbox("Join on", common if common else list(all_dfs[left].columns), key="join_col")
            with jc4: join_how = st.selectbox("Type", ["inner","left","right","outer"], key="join_how")

            if st.button("Apply Join", key="apply_join"):
                try:
                    left_df  = all_dfs[left]
                    right_df = all_dfs[right]
                    # Validate join column exists in both
                    if join_col not in left_df.columns:
                        st.error(f"Column '{join_col}' not found in '{left}'. Available: {list(left_df.columns)}")
                    elif join_col not in right_df.columns:
                        st.error(f"Column '{join_col}' not found in '{right}'. Available: {list(right_df.columns)}")
                    else:
                        merged = pd.merge(left_df, right_df, on=join_col, how=join_how)
                        mk = f"{left}+{right}"
                        all_dfs[mk] = merged
                        st.session_state["all_dfs"] = all_dfs
                        st.session_state["active_df"] = mk
                        st.success(f"Joined → '{mk}': {merged.shape[0]:,} rows × {merged.shape[1]} cols")
                        st.rerun()
                except Exception as e:
                    st.error(f"Join failed: {e}")

    # ── Reset button ──────────────────────────────────────────────────────────
    _, reset_col = st.columns([9, 1])
    with reset_col:
        if st.button("↩ Reset", key="reset_btn"):
            for key in ["all_dfs","active_df","mode","chat_history","explorer_result",
                        "explorer_query","explorer_code","explorer_schema","loaded_file_names"]:
                st.session_state.pop(key, None)
            st.rerun()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab0, tab1, tab2, tab3, tab4 = st.tabs([
        "Dashboard", "Data Explorer", "Chat Analyst", "Anomaly Detector", "What-If Simulator"
    ])

    with tab0:
        render_dashboard_tab(df)

    with tab1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;
                    padding:14px 18px;background:#1A1A1F;border:1px solid #2A2A32;
                    border-left:3px solid #F97316;border-radius:8px;">
            <div>
                <div style="font-family:Sora,sans-serif;font-size:11px;font-weight:600;
                            letter-spacing:0.1em;text-transform:uppercase;color:#F97316;">
                    Data Explorer</div>
                <div style="font-family:Sora,sans-serif;font-size:12px;color:#737373;margin-top:2px;">
                    Ask data questions — get instant charts, tables and AI insights</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_q, col_btn = st.columns([6, 1])
        with col_q:
            pending_q = st.session_state.get("pending_question", "")
            query = st.text_input(
                "query", value=pending_q,
                placeholder="Ask a question about your data...",
                key="nl_query_input", label_visibility="collapsed"
            )
        with col_btn:
            submit_btn = st.button("Analyze", use_container_width=True)

        if pending_q:
            st.session_state["pending_question"] = ""

        if submit_btn and query.strip():
            result, code = execute_nl_query(query, df, schema, sample, extra_dfs=extra_dfs or None)
            if result is not None:
                st.session_state["explorer_result"] = result
                st.session_state["explorer_query"]  = query
                st.session_state["explorer_code"]   = code
                st.session_state["explorer_schema"]  = schema
                # Generate SQL equivalent in background
                with st.spinner("Generating SQL equivalent..."):
                    sql_code = generate_sql_equivalent(query, schema, sample)
                st.session_state["explorer_sql"] = sql_code
            else:
                st.session_state.pop("explorer_result", None)
                st.session_state.pop("explorer_sql", None)
                st.error(code)
        elif submit_btn:
            st.warning("Please enter a question.")

        if "explorer_result" not in st.session_state:
            render_explorer_empty_state()

        if "explorer_result" in st.session_state:
            result  = st.session_state["explorer_result"]
            q       = st.session_state["explorer_query"]
            code    = st.session_state["explorer_code"]
            schema_ = st.session_state["explorer_schema"]

            chart_types = ["Auto","Bar","GroupedBar","MultiBar","Line","Pie","Scatter","Histogram","Table","Metric"]
            override = st.selectbox("Chart type", chart_types, index=0, key="chart_override", label_visibility="collapsed")

            col_chart, col_insight = st.columns([3, 1])
            with col_chart:
                render_chart(result, q, override_type=override)
                with st.expander("Generated code"):
                    pandas_tab, sql_tab = st.tabs(["Pandas", "SQL Equivalent"])
                    with pandas_tab:
                        st.code(code, language="python")
                    with sql_tab:
                        sql_code = st.session_state.get("explorer_sql", "")
                        if sql_code:
                            st.code(sql_code, language="sql")
                        else:
                            st.caption("SQL equivalent not available for this query.")
            with col_insight:
                generate_insight(q, result, schema_)
            generate_why_what_next(q, result, schema_)

    with tab2:
        render_chat_tab(df, extra_dfs=extra_dfs or None)


    with tab3:
        render_anomaly_detector_tab(df)

    with tab4:
        render_what_if_tab(df)


if __name__ == "__main__":
    main()