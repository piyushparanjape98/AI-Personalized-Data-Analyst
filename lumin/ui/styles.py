import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

    :root {
        --bg:        #0C0C0E;
        --surface:   #131316;
        --card:      #1A1A1F;
        --border:    #2A2A32;
        --border2:   #3A3A45;
        --accent:    #F97316;
        --accent-lo: rgba(249,115,22,0.12);
        --teal:      #2DD4BF;
        --teal-lo:   rgba(45,212,191,0.1);
        --violet:    #A78BFA;
        --text:      #F0F0F2;
        --text2:     #9090A0;
        --text3:     #50505E;
        --success:   #34D399;
        --error:     #F87171;
        --body:      'Sora', -apple-system, BlinkMacSystemFont, sans-serif;
        --mono:      'JetBrains Mono', monospace;
        --r:         10px;
        --r2:        14px;
    }

    *, *::before, *::after { box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        font-family: var(--body) !important;
        color: var(--text) !important;
    }

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] { display: none !important; }

    .main .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ── TOP BAR ── */
    .lumin-topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px; height: 60px;
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        position: sticky; top: 0; z-index: 100;
    }
    .lumin-brand {
        font-family: var(--body); font-size: 17px; font-weight: 600;
        color: var(--text); letter-spacing: -0.01em;
    }
    .lumin-brand span { color: var(--accent); }
    .lumin-tagline {
        font-family: var(--body); font-size: 11px; font-weight: 300;
        color: var(--text3); margin-top: 2px; letter-spacing: 0.02em;
    }
    .lumin-status {
        font-family: var(--mono); font-size: 10px;
        color: var(--text3); letter-spacing: 0.08em;
        display: flex; align-items: center; gap: 7px;
    }

    /* ── TABS ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 0 !important; padding: 0 40px !important; border-radius: 0 !important;
    }
    [data-testid="stTabs"] [role="tab"] {
        font-family: var(--body) !important; font-size: 13px !important;
        font-weight: 400 !important; color: var(--text3) !important;
        border: none !important; border-radius: 0 !important;
        padding: 14px 22px !important;
        border-bottom: 2px solid transparent !important;
        margin-bottom: -1px !important; transition: all 0.15s !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--accent) !important; font-weight: 500 !important;
        border-bottom-color: var(--accent) !important; background: transparent !important;
    }
    [data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]) {
        color: var(--text) !important; background: transparent !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
    [data-testid="stTabs"] [role="tabpanel"] { padding: 32px 40px !important; }

    /* ── HEADINGS ── */
    h1,h2,h3,h4,h5 { font-family: var(--body) !important; color: var(--text) !important; }
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }
    h2 { font-size: 1.2rem !important; font-weight: 500 !important; }
    h3,h4,h5 { font-weight: 500 !important; }

    /* ── BUTTONS ── */
    .stButton > button {
        font-family: var(--body) !important; font-weight: 500 !important;
        font-size: 13px !important; letter-spacing: 0.01em !important;
        background: var(--accent) !important; color: #0C0C0E !important;
        border: none !important; border-radius: var(--r) !important;
        padding: 10px 24px !important; transition: all 0.15s !important;
        box-shadow: 0 2px 14px rgba(249,115,22,0.28) !important;
    }
    .stButton > button:hover {
        background: #FB923C !important;
        box-shadow: 0 4px 20px rgba(249,115,22,0.42) !important;
        transform: translateY(-1px) !important;
    }

    /* ── TEXT INPUT ── */
    .stTextInput > div > div > input {
        background: var(--card) !important; border: 1px solid var(--border2) !important;
        border-radius: var(--r) !important; color: var(--text) !important;
        font-family: var(--body) !important; font-size: 14px !important;
        padding: 12px 16px !important; transition: border-color 0.15s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important; outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--text3) !important; }

    /* ── CHAT INPUT ── */
    [data-testid="stChatInput"] > div {
        background: var(--card) !important; border: 1px solid var(--border2) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"]:focus-within > div {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 3px var(--teal-lo) !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: var(--body) !important; font-size: 14px !important;
        color: var(--text) !important; background: transparent !important;
    }

    /* ── SELECTBOX ── */
    .stSelectbox > div > div {
        background: var(--card) !important; border: 1px solid var(--border2) !important;
        border-radius: var(--r) !important; color: var(--text) !important;
        font-family: var(--body) !important; font-size: 13px !important;
    }

    /* ── LABELS ── */
    .stTextInput label, .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stFileUploader label, .stRadio > label {
        font-family: var(--body) !important; font-size: 11px !important;
        font-weight: 400 !important; color: var(--text3) !important; margin-bottom: 6px !important;
    }

    /* ── DATAFRAMES ── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--r2) !important; overflow: hidden !important;
    }
    [data-testid="stDataFrame"] thead tr th {
        background: var(--surface) !important; color: var(--accent) !important;
        font-family: var(--mono) !important; font-size: 10px !important;
        font-weight: 500 !important; letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid var(--border2) !important; padding: 10px 14px !important;
    }
    [data-testid="stDataFrame"] tbody tr td {
        background: var(--card) !important; color: var(--text) !important;
        font-family: var(--mono) !important; font-size: 12px !important;
        border-color: var(--border) !important; padding: 8px 14px !important;
    }
    [data-testid="stDataFrame"] tbody tr:hover td { background: var(--surface) !important; }

    /* ── METRICS ── */
    [data-testid="stMetric"] {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--r2) !important; padding: 20px 24px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--accent) !important;
        box-shadow: 0 0 22px rgba(249,115,22,0.07) !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-family: var(--body) !important; font-size: 10px !important;
        font-weight: 500 !important; letter-spacing: 0.06em !important;
        text-transform: uppercase !important; color: var(--text3) !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: var(--body) !important; font-size: 26px !important;
        font-weight: 600 !important; color: var(--text) !important;
    }

    /* ── EXPANDER ── */
    [data-testid="stExpander"] {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--r2) !important; overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
        font-family: var(--body) !important; font-size: 12px !important;
        font-weight: 500 !important; color: var(--text2) !important; padding: 13px 18px !important;
    }
    [data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

    /* ── CODE ── */
    code, pre, .stCode {
        font-family: var(--mono) !important; background: var(--surface) !important;
        border: 1px solid var(--border) !important; border-radius: var(--r) !important;
        font-size: 12px !important;
    }

    /* ── ALERTS ── */
    .stSuccess { background: rgba(52,211,153,0.07) !important; border-color: var(--success) !important; border-radius: var(--r) !important; }
    .stError   { background: rgba(248,113,113,0.07) !important; border-color: var(--error) !important;   border-radius: var(--r) !important; }
    .stWarning { background: rgba(249,115,22,0.07) !important;  border-color: var(--accent) !important;  border-radius: var(--r) !important; }
    .stInfo    { background: rgba(167,139,250,0.07) !important; border-color: var(--violet) !important;  border-radius: var(--r) !important; }

    /* ── CHAT MESSAGES ── */
    [data-testid="stChatMessage"] {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--r2) !important; padding: 16px 20px !important; margin-bottom: 8px !important;
    }

    /* ── MULTISELECT TAGS ── */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: var(--accent-lo) !important; border: 1px solid rgba(249,115,22,0.3) !important;
        color: var(--accent) !important; font-family: var(--mono) !important;
        font-size: 10px !important; border-radius: 5px !important;
    }

    /* ── SLIDER ── */
    [data-testid="stSlider"] [role="slider"] {
        background: var(--accent) !important; border: 2px solid var(--bg) !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,0.3) !important;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] {
        background: var(--card) !important; border: 1.5px dashed var(--border2) !important;
        border-radius: var(--r2) !important; transition: border-color 0.15s !important;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    /* ── HIDE CHROME ── */
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
    hr { border-color: var(--border) !important; }
                
    /* Force desktop view on mobile */
    [data-testid="stAppViewContainer"] {
    min-width: 1024px !important;
    }
    </style>
    """, unsafe_allow_html=True)