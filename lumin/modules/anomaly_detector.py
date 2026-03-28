import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from prompts.templates import anomaly_prompt
from modules.nl_query import ask_groq


def detect_iqr(df, num_cols):
    anomalies = pd.DataFrame(index=df.index)
    bounds = {}
    for col in num_cols:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        lo, hi = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        anomalies[col] = (df[col] < lo) | (df[col] > hi)
        bounds[col] = (lo, hi)
    return anomalies, bounds


def detect_iso(df, num_cols):
    anomalies = pd.DataFrame(index=df.index, columns=num_cols)
    for col in num_cols:
        valid_idx = df[col].dropna().index
        if len(valid_idx) > 10:
            iso = IsolationForest(contamination=0.05, random_state=42)
            preds = iso.fit_predict(df.loc[valid_idx, [col]])
            anomalies.loc[valid_idx, col] = preds == -1
        else:
            anomalies[col] = False
    return anomalies.fillna(False)


def render_anomaly_detector_tab(df: pd.DataFrame):
    st.header("Anomaly Detector")

    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        st.warning("No numeric columns available.")
        return

    st.markdown("""
    <div style="padding:14px 18px;background:#1A1A1F;border:1px solid #2A2A32;
                border-left:3px solid #F87171;border-radius:8px;margin-bottom:24px;">
        <div style="font-family:Sora,sans-serif;font-size:11px;font-weight:600;
                    letter-spacing:0.1em;text-transform:uppercase;color:#F87171;">Anomaly Detector</div>
        <div style="font-family:Sora,sans-serif;font-size:12px;color:#70707E;margin-top:3px;">
            IQR flags statistical outliers beyond 1.5× the interquartile range.
            Isolation Forest uses ML to find structurally unusual points.
            <strong style="color:#A1A1AA;">Both methods are correct — they measure different things.</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Run both methods always ───────────────────────────────────────────────
    iqr_mask, bounds = detect_iqr(df, num_cols)
    iso_mask         = detect_iso(df, num_cols)

    iqr_counts = iqr_mask.sum()
    iso_counts = iso_mask.astype(bool).sum()

    # ── Summary comparison table ──────────────────────────────────────────────
    st.markdown("##### Method Comparison")
    summary_rows = []
    for col in num_cols:
        iqr_n = int(iqr_counts[col])
        iso_n = int(iso_counts[col])
        agree = int((iqr_mask[col] & iso_mask[col].astype(bool)).sum())
        summary_rows.append({
            "Column": col,
            "IQR Anomalies": iqr_n,
            "Isolation Forest": iso_n,
            "Both Agree": agree,
            "IQR Bounds": f"[{bounds[col][0]:.2f}, {bounds[col][1]:.2f}]"
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # ── Column selector ───────────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    active_cols = [c for c in num_cols if iqr_counts[c] > 0 or iso_counts[c] > 0]
    if not active_cols:
        st.success("No anomalies detected in any column.")
        return

    selected_col = st.selectbox("Investigate column:", active_cols)

    # ── Side by side scatter: IQR vs Isolation Forest ────────────────────────
    st.markdown(f"##### Anomaly Plots — `{selected_col}`")
    c1, c2 = st.columns(2)

    idx = df.reset_index().index
    vals = df[selected_col].values

    with c1:
        st.markdown('<div style="font-family:Sora,sans-serif;font-size:11px;color:#F97316;'
                    'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">IQR Method</div>',
                    unsafe_allow_html=True)
        iqr_scatter = pd.DataFrame({
            "Index": idx, "Value": vals,
            "Anomaly": iqr_mask[selected_col].values.astype(str)
        })
        fig1 = px.scatter(iqr_scatter, x="Index", y="Value", color="Anomaly",
            color_discrete_map={"False": "#3A3A45", "True": "#F97316"},
            title=f"IQR: {int(iqr_counts[selected_col])} anomalies")
        lo, hi = bounds[selected_col]
        fig1.add_hline(y=hi, line_dash="dash", line_color="#F87171", annotation_text="Upper bound")
        fig1.add_hline(y=lo, line_dash="dash", line_color="#F87171", annotation_text="Lower bound")
        fig1.update_layout(
            plot_bgcolor="#0C0C0E", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F0F2", family="Sora,sans-serif", size=11),
            showlegend=False, margin=dict(l=16,r=16,t=40,b=16),
            xaxis=dict(gridcolor="#2A2A32"), yaxis=dict(gridcolor="#2A2A32"),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.markdown('<div style="font-family:Sora,sans-serif;font-size:11px;color:#A78BFA;'
                    'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">Isolation Forest</div>',
                    unsafe_allow_html=True)
        iso_scatter = pd.DataFrame({
            "Index": idx, "Value": vals,
            "Anomaly": iso_mask[selected_col].astype(bool).astype(str)
        })
        fig2 = px.scatter(iso_scatter, x="Index", y="Value", color="Anomaly",
            color_discrete_map={"False": "#3A3A45", "True": "#A78BFA"},
            title=f"Isolation Forest: {int(iso_counts[selected_col])} anomalies")
        fig2.update_layout(
            plot_bgcolor="#0C0C0E", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F0F2", family="Sora,sans-serif", size=11),
            showlegend=False, margin=dict(l=16,r=16,t=40,b=16),
            xaxis=dict(gridcolor="#2A2A32"), yaxis=dict(gridcolor="#2A2A32"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Agreed anomalies (both methods) ──────────────────────────────────────
    agreed_mask = iqr_mask[selected_col] & iso_mask[selected_col].astype(bool)
    agreed_rows = df[agreed_mask]

    st.markdown(f"##### Rows flagged by BOTH methods ({len(agreed_rows)})")
    if len(agreed_rows) > 0:
        st.dataframe(agreed_rows, use_container_width=True)
    else:
        st.info("No rows were flagged by both methods simultaneously — the methods detected different outlier types.")

    # ── AI Explanation ────────────────────────────────────────────────────────
    if st.button("Generate AI Explanation", key="btn_anomaly"):
        sample_iqr = df[iqr_mask[selected_col]][selected_col].dropna().head(5).tolist()
        sample_iso = df[iso_mask[selected_col].astype(bool)][selected_col].dropna().head(5).tolist()
        col_summary = (
            f"Column: {selected_col}\n"
            f"IQR anomalies: {int(iqr_counts[selected_col])} | bounds: {bounds[selected_col][0]:.2f} to {bounds[selected_col][1]:.2f}\n"
            f"Sample IQR outlier values: {sample_iqr}\n"
            f"Isolation Forest anomalies: {int(iso_counts[selected_col])}\n"
            f"Sample Isolation Forest outlier values: {sample_iso}\n"
            f"Both methods agree on: {len(agreed_rows)} rows"
        )
        prompt = anomaly_prompt(col_summary)
        with st.spinner("Analyzing..."):
            explanation = ask_groq(prompt)
        if explanation:
            st.info(f"**AI Anomaly Interpretation**\n\n{explanation}")