import streamlit as st


def inject_css():
    st.markdown(
        """
<style>
/* ── Import ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0e1117;
    --surface:   #1a1d2e;
    --surface2:  #252840;
    --accent:    #34d679;
    --accent2:   #4fffab;
    --warn:      #f59e0b;
    --danger:    #ef4444;
    --text:      #e8eaf0;
    --muted:     #8892b0;
    --radius:    12px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--surface2);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Cards ── */
.habit-card {
    background: var(--surface);
    border: 1px solid var(--surface2);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: border-color .2s;
}
.habit-card:hover { border-color: var(--accent); }

/* ── Metric tiles ── */
.metric-tile {
    background: var(--surface);
    border: 1px solid var(--surface2);
    border-radius: var(--radius);
    padding: 1rem;
    text-align: center;
}
.metric-num {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.metric-label { font-size: .8rem; color: var(--muted); margin-top: .3rem; }

/* ── Streak counter ── */
.streak-fire {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
}

/* ── Badge grid ── */
.badge-grid { display: flex; flex-wrap: wrap; gap: .7rem; }
.badge-item {
    background: var(--surface2);
    border-radius: 50px;
    padding: .4rem .9rem;
    font-size: .85rem;
    display: flex; align-items: center; gap: .4rem;
}
.badge-item.locked { opacity: .35; filter: grayscale(1); }
.badge-item.unlocked { border: 1px solid var(--accent); }

/* ── Progress bar override ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    border-radius: 99px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #0e1117 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    transition: opacity .2s;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Secondary button ── */
.stButton.secondary > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
}

/* ── Checkbox ── */
.stCheckbox > label { font-size: 1rem; }

/* ── Selectbox / text input ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stTimeInput > div > div > input {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-color: #3a3f5c !important;
    border-radius: 8px !important;
}

/* ── Section divider ── */
hr { border-color: var(--surface2) !important; }

/* ── Expander ── */
details { background: var(--surface) !important; border-radius: var(--radius) !important; }

/* ── Alert / success banner ── */
.stAlert { border-radius: var(--radius) !important; }

/* ── Tab strip ── */
button[data-baseweb="tab"] {
    color: var(--muted) !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 3px; }
</style>
""",
        unsafe_allow_html=True,
    )