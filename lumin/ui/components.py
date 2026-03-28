import streamlit as st
import pandas as pd

F_BODY = "Sora,-apple-system,BlinkMacSystemFont,sans-serif"
F_MONO = "JetBrains Mono,monospace"


def render_topbar(api_ok: bool, df: pd.DataFrame = None):
    dot   = "#34D399" if api_ok else "#F87171"
    label = "API connected" if api_ok else "API missing"
    stats = ""  # always defined

    html = (
        '<div class="lumin-topbar">'
          # Left: brand
          '<div>'
            '<div class="lumin-brand">AI: <span>Personalized</span> Data Analyst</div>'
          '</div>'
          # Center: tagline — prominent
          '<div style="position:absolute;left:50%;transform:translateX(-50%);text-align:center;">'
            '<div style="font-family:Sora,sans-serif;font-size:13px;font-weight:400;'
            'color:#A1A1AA;letter-spacing:0.02em;white-space:nowrap;">'
            'Upload your Data &nbsp;<span style="color:#3A3A45;">·</span>&nbsp; '
            'Ask anything &nbsp;<span style="color:#3A3A45;">·</span>&nbsp; '
            '<span style="color:#F97316;">Understand Everything</span>'
            '</div>'
          '</div>'
          # Right: status
          '<div style="display:flex;gap:20px;align-items:center;">'
            + stats +
            '<div class="lumin-status">'
              '<span style="width:7px;height:7px;border-radius:50%;display:inline-block;'
              'background:' + dot + ';box-shadow:0 0 8px ' + dot + ';"></span>'
              '&nbsp;' + label +
            '</div>'
          '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_data_strip(df: pd.DataFrame):
    num_count  = len(df.select_dtypes(include="number").columns)
    cat_count  = len(df.select_dtypes(exclude="number").columns)
    null_count = int(df.isnull().sum().sum())
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:  st.metric("Rows",           f"{df.shape[0]:,}")
    with c2:  st.metric("Columns",        df.shape[1])
    with c3:  st.metric("Numeric",        num_count)
    with c4:  st.metric("Categorical",    cat_count)
    with c5:  st.metric("Missing Values", null_count)


def render_upload_screen():
    """Full centered upload landing page."""
    st.markdown(
        '<div style="text-align:center;padding:80px 20px 0;">'

          # Pill badge
          '<div style="display:inline-block;background:rgba(249,115,22,0.12);'
          'border:1px solid rgba(249,115,22,0.3);border-radius:99px;'
          'padding:5px 16px;margin-bottom:28px;">'
            '<span style="font-family:' + F_BODY + ';font-size:11px;font-weight:500;'
            'letter-spacing:0.08em;text-transform:uppercase;color:#F97316;">AI-Powered Analytics</span>'
          '</div>'

          # Headline
          '<div style="font-family:' + F_BODY + ';font-size:42px;font-weight:700;'
          'color:#F0F0F2;letter-spacing:-0.03em;line-height:1.15;margin-bottom:14px;">'
            'Your Personal<br>'
            '<span style="color:#F97316;">Data Analyst</span>'
          '</div>'

          # Subtitle
          '<div style="font-family:' + F_BODY + ';font-size:16px;font-weight:300;'
          'color:#70707E;max-width:420px;margin:0 auto 52px;line-height:1.7;">'
            'Upload a CSV or Excel file. Ask questions in plain English.<br>'
            'Get charts, insights and decisions instantly.'
          '</div>'

        '</div>',
        unsafe_allow_html=True
    )


def render_explorer_empty_state():
    """Illustrated empty state for Data Explorer."""
    st.markdown(
        '<div style="text-align:center;padding:52px 20px 32px;">'

          # SVG illustration
          '<svg width="300" height="160" viewBox="0 0 300 160" fill="none" '
          'xmlns="http://www.w3.org/2000/svg" style="margin:0 auto 24px;display:block;">'

            # Grid
            '<line x1="0" y1="40"  x2="300" y2="40"  stroke="#2A2A32" stroke-width="1"/>'
            '<line x1="0" y1="80"  x2="300" y2="80"  stroke="#2A2A32" stroke-width="1"/>'
            '<line x1="0" y1="120" x2="300" y2="120" stroke="#2A2A32" stroke-width="1"/>'

            # Bars - gradient feel via opacity
            '<rect x="16"  y="95"  width="30" height="65" rx="5" fill="#F97316" opacity="0.2"/>'
            '<rect x="56"  y="65"  width="30" height="95" rx="5" fill="#F97316" opacity="0.45"/>'
            '<rect x="96"  y="38"  width="30" height="122" rx="5" fill="#F97316" opacity="0.9"/>'
            '<rect x="136" y="72"  width="30" height="88"  rx="5" fill="#F97316" opacity="0.45"/>'
            '<rect x="176" y="100" width="30" height="60"  rx="5" fill="#F97316" opacity="0.2"/>'

            # Value labels on tallest bar
            '<text x="111" y="30" font-family="' + F_MONO + '" font-size="9" fill="#F97316" text-anchor="middle">peak</text>'

            # Teal line chart
            '<polyline points="228,128 245,88 262,102 279,55" '
            'stroke="#2DD4BF" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="228" cy="128" r="4" fill="#2DD4BF"/>'
            '<circle cx="245" cy="88"  r="4" fill="#2DD4BF"/>'
            '<circle cx="262" cy="102" r="4" fill="#2DD4BF"/>'
            '<circle cx="279" cy="55"  r="5" fill="#2DD4BF" opacity="0.9"/>'

            # Trend arrow
            '<line x1="228" y1="128" x2="279" y2="55" stroke="#2DD4BF" stroke-width="1" stroke-dasharray="3 3" opacity="0.3"/>'

          '</svg>'

          '<div style="font-family:' + F_BODY + ';font-size:16px;font-weight:500;'
          'color:#9090A0;margin-bottom:8px;">Ask a question to see your chart</div>'

          '<div style="font-family:' + F_BODY + ';font-size:13px;font-weight:300;'
          'color:#50505E;line-height:1.6;max-width:340px;margin:0 auto;">'
            'Type anything above — <strong style="color:#F97316;font-weight:500;">Analyze</strong> '
            'will write the code, run it, and render the result.'
          '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def render_dashboard_tab(df: pd.DataFrame):
    st.markdown("##### Sample Data")
    st.dataframe(df.head(10), use_container_width=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("##### Column Types")
        st.dataframe(
            pd.DataFrame({"Column": df.columns, "Type": df.dtypes.astype(str).values}),
            use_container_width=True, hide_index=True
        )
    with col2:
        st.markdown("##### Missing Values")
        missing = df.isnull().sum()
        st.dataframe(
            pd.DataFrame({
                "Column": missing.index, "Missing": missing.values,
                "%": (missing / len(df) * 100).round(1).astype(str) + "%",
            }),
            use_container_width=True, hide_index=True
        )
    with col3:
        st.markdown("##### Numeric Summary")
        num_df = df.select_dtypes(include="number")
        if not num_df.empty:
            desc = num_df.describe().T[["mean","std","min","max"]].round(2).reset_index()
            desc.columns = ["Column","Mean","Std","Min","Max"]
            st.dataframe(desc, use_container_width=True, hide_index=True)
        else:
            st.info("No numeric columns.")