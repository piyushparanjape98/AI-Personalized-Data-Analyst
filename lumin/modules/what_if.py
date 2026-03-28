import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from prompts.templates import what_if_prompt
from modules.nl_query import ask_groq


def render_what_if_tab(df: pd.DataFrame):
    st.header("What-If Simulator")

    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        st.warning("No numeric columns available for simulation.")
        return

    # ── Mode banner ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:14px 18px;background:#1A1A1F;border:1px solid #2A2A32;
                border-left:3px solid #A78BFA;border-radius:8px;margin-bottom:24px;">
        <div style="font-family:Sora,sans-serif;font-size:11px;font-weight:600;
                    letter-spacing:0.1em;text-transform:uppercase;color:#A78BFA;">
            What-If Simulator</div>
        <div style="font-family:Sora,sans-serif;font-size:12px;color:#70707E;margin-top:3px;">
            Adjust any column by percentage — see how correlated columns react in real time</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Column selector ───────────────────────────────────────────────────────
    selected_cols = st.multiselect(
        "Columns to simulate:",
        options=num_cols,
        default=[num_cols[0]],
        max_selections=4,
        key="whatif_cols"
    )

    if not selected_cols:
        st.info("Select at least one column to simulate.")
        return

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Percentage sliders ────────────────────────────────────────────────────
    # Each selected col gets a % change slider from -80% to +150%
    adjustments = {}
    slider_cols = st.columns(len(selected_cols))

    for i, col in enumerate(selected_cols):
        orig_mean = df[col].mean()
        if pd.isna(orig_mean) or orig_mean == 0:
            with slider_cols[i]:
                st.warning(f"'{col}' mean is 0 or NaN.")
            continue

        with slider_cols[i]:
            pct_change = st.slider(
                f"{col}",
                min_value=-80,
                max_value=150,
                value=0,
                step=5,
                format="%d%%",
                key=f"whatif_pct_{col}",
            )
            sim_mean = orig_mean * (1 + pct_change / 100)

            # Color indicator
            if pct_change > 0:
                color = "#34D399"
                arrow = "▲"
            elif pct_change < 0:
                color = "#F87171"
                arrow = "▼"
            else:
                color = "#9090A0"
                arrow = "─"

            st.markdown(
                f'<div style="text-align:center;margin-top:4px;">'
                f'<span style="font-family:Sora,sans-serif;font-size:22px;font-weight:700;color:{color};">'
                f'{arrow} {pct_change:+d}%</span><br>'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#52525B;">'
                f'{orig_mean:,.2f} → {sim_mean:,.2f}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            adjustments[col] = {
                "original": orig_mean,
                "simulated": sim_mean,
                "pct_change": pct_change,
                "scale": 1 + pct_change / 100,
            }

    if not adjustments:
        return

    # ── Compute simulated df ──────────────────────────────────────────────────
    simulated_df = df.copy()
    correlations = df[num_cols].corr()

    # Apply direct changes
    for col, adj in adjustments.items():
        simulated_df[col] = simulated_df[col] * adj["scale"]

    # Propagate correlated effects
    for col, adj in adjustments.items():
        corr_series = correlations[col]
        for c in num_cols:
            if c not in adjustments:
                corr_val = corr_series[c]
                if abs(corr_val) > 0.05:  # lower threshold = more sensitive
                    ripple = (adj["scale"] - 1) * corr_val
                    simulated_df[c] = simulated_df[c] * (1 + ripple)

    # ── Impact summary ────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("##### Impact on All Columns")

    impact_rows = []
    for c in num_cols:
        orig  = df[c].mean()
        sim   = simulated_df[c].mean()
        delta_pct = ((sim - orig) / orig * 100) if orig != 0 else 0
        kind  = "🎛 Controlled" if c in adjustments else "📈 Affected"
        impact_rows.append({
            "Column": c,
            "Original": round(orig, 2),
            "Simulated": round(sim, 2),
            "Change %": f"{delta_pct:+.1f}%",
            "Type": kind,
        })

    impact_df = pd.DataFrame(impact_rows)
    st.dataframe(impact_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Animated before/after bar chart for ALL numeric cols ─────────────────
    st.markdown("##### Before vs After — All Columns")

    orig_means = [df[c].mean() for c in num_cols]
    sim_means  = [simulated_df[c].mean() for c in num_cols]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Original",
        x=num_cols,
        y=orig_means,
        marker_color="rgba(144,144,160,0.5)",
        marker_line_color="rgba(144,144,160,0.8)",
        marker_line_width=1,
    ))
    fig_bar.add_trace(go.Bar(
        name="Simulated",
        x=num_cols,
        y=sim_means,
        marker=dict(
            color=[
                "#34D399" if s > o else ("#F87171" if s < o else "#9090A0")
                for o, s in zip(orig_means, sim_means)
            ],
            opacity=0.85,
        ),
    ))
    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="#0C0C0E",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F0F0F2", family="Sora,sans-serif", size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#2A2A32", linecolor="#2A2A32"),
        yaxis=dict(gridcolor="#2A2A32", linecolor="#2A2A32"),
        margin=dict(l=16, r=16, t=32, b=16),
        transition={"duration": 600, "easing": "cubic-in-out"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Distribution overlays for selected cols ───────────────────────────────
    st.markdown("##### Distribution Shift")

    dist_cols = st.columns(min(len(selected_cols), 2))
    for i, col in enumerate(selected_cols):
        with dist_cols[i % 2]:
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df[col], name="Original",
                opacity=0.55, marker_color="#9090A0", nbinsx=30
            ))
            fig.add_trace(go.Histogram(
                x=simulated_df[col], name="Simulated",
                opacity=0.75,
                marker_color="#F97316" if adjustments[col]["pct_change"] >= 0 else "#F87171",
                nbinsx=30
            ))
            fig.update_layout(
                barmode="overlay",
                title=f"{col}  {adjustments[col]['pct_change']:+d}%",
                plot_bgcolor="#0C0C0E",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F0F0F2", family="Sora,sans-serif", size=11),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#2A2A32"),
                yaxis=dict(gridcolor="#2A2A32"),
                margin=dict(l=16, r=16, t=40, b=16),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Ripple effect chart — affected columns only ───────────────────────────
    affected = [r for r in impact_rows if r["Type"] == "📈 Affected"]
    if affected:
        st.markdown("##### Ripple Effect on Correlated Columns")
        aff_names = [r["Column"] for r in affected]
        aff_deltas = [float(r["Change %"].replace("%","").replace("+","")) for r in affected]

        colors = ["#34D399" if d > 0 else "#F87171" for d in aff_deltas]

        fig_ripple = go.Figure(go.Bar(
            x=aff_names,
            y=aff_deltas,
            marker_color=colors,
            marker_opacity=0.8,
            text=[f"{d:+.1f}%" for d in aff_deltas],
            textposition="outside",
            textfont=dict(size=11, color="#F0F0F2"),
        ))
        fig_ripple.update_layout(
            plot_bgcolor="#0C0C0E",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F0F2", family="Sora,sans-serif", size=11),
            xaxis=dict(gridcolor="#2A2A32", linecolor="#2A2A32"),
            yaxis=dict(gridcolor="#2A2A32", linecolor="#2A2A32", ticksuffix="%"),
            margin=dict(l=16, r=16, t=32, b=16),
            showlegend=False,
        )
        fig_ripple.add_hline(y=0, line_color="#3A3A45", line_width=1)
        st.plotly_chart(fig_ripple, use_container_width=True)

    # ── Correlation heatmap ───────────────────────────────────────────────────
    with st.expander("View Correlation Heatmap"):
        fig_corr = px.imshow(
            correlations, text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Column Correlations", aspect="auto"
        )
        fig_corr.update_layout(
            plot_bgcolor="#0C0C0E", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F0F2", family="Sora,sans-serif", size=11),
            margin=dict(l=16, r=16, t=48, b=16),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # ── AI Impact Analysis ────────────────────────────────────────────────────
    if st.button("Generate AI Impact Analysis", key="btn_whatif_ai"):
        affected_stats = "; ".join([
            f"{r['Column']}: {r['Original']} → {r['Simulated']} ({r['Change %']})"
            for r in impact_rows if r["Type"] == "📈 Affected"
        ])
        prompt = what_if_prompt(
            column=", ".join(selected_cols),
            original_mean=list(adjustments.values())[0]["original"],
            simulated_mean=list(adjustments.values())[0]["simulated"],
            delta_pct=list(adjustments.values())[0]["pct_change"],
            affected_stats=affected_stats
        )
        with st.spinner("Analyzing impact..."):
            explanation = ask_groq(prompt)
        if explanation:
            st.info(f"**AI Impact Analysis**\n\n{explanation}")