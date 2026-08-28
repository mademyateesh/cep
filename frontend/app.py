"""
UnifiedGov — Streamlit frontend.
Theme: Civic Teal & Terracotta (matches the Student Innovation Program deck).
Run: streamlit run app.py   (with the API running on localhost:8000)
"""
import requests
import streamlit as st

API_BASE_URL = "https://cep-h2v8.onrender.com"

st.set_page_config(page_title="UnifiedGov", page_icon="🏛️", layout="wide")

# ---------------------------------------------------------------------
# Theme tokens — Civic Teal & Terracotta
# ---------------------------------------------------------------------
TEAL = "#14B8A6"
TEAL_DARK = "#0D9488"
TERRACOTTA = "#E2725B"
AMBER = "#F5A623"
EMERALD = "#22C55E"
ROSE = "#F43F5E"
SLATE = "#94A3B8"
INK = "#0B1220"
CARD = "#111A2E"

STATUS_STYLE = {
    "open": (EMERALD, "🟢 Open"),
    "closing_soon": (AMBER, "🟡 Closing Soon"),
    "closed": (ROSE, "🔴 Closed"),
    "upcoming": (SLATE, "⚪ Upcoming"),
}

# ---------------------------------------------------------------------
# Global CSS — gradients, hover-lift cards, pulsing badge, styled buttons
# ---------------------------------------------------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* --- FULL SCREEN EXPANSION --- */
.block-container, div[data-testid="stMainBlockContainer"] {{
    max-width: 100% !important;
    padding-top: 5.5rem !important;
    padding-bottom: 5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}

/* Page background */
.stApp {{
    background: radial-gradient(circle at 15% 0%, rgba(20,184,166,0.10), transparent 45%),
                radial-gradient(circle at 85% 15%, rgba(226,114,91,0.10), transparent 40%),
                {INK};
}}

/* Gradient hero title - Centered */
.ug-hero-title {{
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    line-height: 1.1;
    text-align: center;
    background: linear-gradient(90deg, {TEAL} 0%, {AMBER} 55%, {TERRACOTTA} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
    animation: ug-fade-in 0.6s ease-out;
}}

/* Subtitle - Centered */
.ug-hero-sub {{
    color: {SLATE};
    font-size: 1.05rem;
    text-align: center;
    margin-bottom: 1.5rem;
    animation: ug-fade-in 0.8s ease-out;
}}

@keyframes ug-fade-in {{
    from {{ opacity: 0; transform: translateY(-6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes ug-pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(245,166,35,0.55); }}
    70%  {{ box-shadow: 0 0 0 8px rgba(245,166,35,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(245,166,35,0); }}
}}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 16px !important;
    border: 1px solid rgba(148,163,184,0.18) !important;
    background: linear-gradient(160deg, {CARD} 0%, rgba(17,26,46,0.6) 100%);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(20,184,166,0.15);
    border-color: rgba(20,184,166,0.45) !important;
}}

/* Buttons */
.stButton > button, .stLinkButton > a {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: 1px solid rgba(148,163,184,0.25) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}}
.stButton > button:hover, .stLinkButton > a:hover {{
    transform: translateY(-2px);
    border-color: {TEAL} !important;
    box-shadow: 0 6px 16px rgba(20,184,166,0.25);
}}
.stButton > button[kind="primary"], .stLinkButton > a[kind="primary"] {{
    background: linear-gradient(90deg, {TERRACOTTA}, {AMBER}) !important;
    border: none !important;
    color: white !important;
}}
.stButton > button[kind="primary"]:hover, .stLinkButton > a[kind="primary"]:hover {{
    box-shadow: 0 6px 18px rgba(226,114,91,0.35);
}}

/* Status pill */
.ug-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    color: white;
}}
.ug-pill-pulse {{ animation: ug-pulse 2s infinite; }}

.ug-box-title {{
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.25rem;
    margin-bottom: 4px;
}}
.ug-box-icon {{
    font-size: 3rem;
    margin-bottom: 6px;
    display: block;
}}
</style>
""",
    unsafe_allow_html=True,
)


def status_pill(status: str) -> str:
    color, label = STATUS_STYLE.get(status, (SLATE, status))
    pulse_class = "ug-pill-pulse" if status == "closing_soon" else ""
    return f'<span class="ug-pill {pulse_class}" style="background:{color};">{label}</span>'


# ---------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------

@st.cache_data(ttl=60)
def api_get(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params or {}, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the API at {API_BASE}. Is `uvicorn main:app --reload --port 8000` running?\n\n{e}")
        return []


# ---------------------------------------------------------------------
# Session state — controls which "box" the user is browsing
# ---------------------------------------------------------------------

if "view" not in st.session_state:
    st.session_state.view = "home"       # home | all | state | central
if "state_slug" not in st.session_state:
    st.session_state.state_slug = None   # selected state, once in state-wise view
if "org_slug" not in st.session_state:
    st.session_state.org_slug = None     # selected central org, once in central-wise view
if "exam_slug" not in st.session_state:
    st.session_state.exam_slug = None    # selected exam, for detail view


def go_home():
    st.session_state.view = "home"
    st.session_state.state_slug = None
    st.session_state.org_slug = None
    st.session_state.exam_slug = None


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.markdown('<div class="ug-hero-title">🏛️ UnifiedGov</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ug-hero-sub">A unified aggregator for Indian government exams—connecting aspirants ' \
    'directly to verified official application portals.</div>',
    unsafe_allow_html=True,
)

if st.session_state.view != "home":
    if st.button("← Back to Home"):
        go_home()
        st.rerun()

st.divider()

# ---------------------------------------------------------------------
# HOME — three boxes: All / State-wise / Central-wise
# ---------------------------------------------------------------------

def render_home():
    st.subheader("Browse Exams")

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(
                f'<span class="ug-box-icon">📋</span>'
                f'<div class="ug-box-title" style="color:{AMBER};">All Exams</div>',
                unsafe_allow_html=True,
            )
            st.write("Every listing across every state and central organization.")
            if st.button("Browse All", use_container_width=True, key="btn_all", type="primary"):
                st.session_state.view = "all"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown(
                f'<span class="ug-box-icon">🗺️</span>'
                f'<div class="ug-box-title" style="color:{TEAL};">State-wise</div>',
                unsafe_allow_html=True,
            )
            st.write("Filter exams by state — all 28 states + 8 union territories.")
            if st.button("Browse by State", use_container_width=True, key="btn_state"):
                st.session_state.view = "state"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.markdown(
                f'<span class="ug-box-icon">🇮🇳</span>'
                f'<div class="ug-box-title" style="color:{TERRACOTTA};">Central-wise</div>',
                unsafe_allow_html=True,
            )
            st.write("Filter exams by central organization — SSC, IBPS, UPSC, RRB.")
            if st.button("Browse Central", use_container_width=True, key="btn_central"):
                st.session_state.view = "central"
                st.rerun()

    st.divider()
    st.subheader("⏰ Closing Soon")
    closing = api_get("/exams/closing-soon", {"days": 7})
    if closing:
        for exam in closing:
            render_exam_row(exam)
    else:
        st.info("Nothing closing in the next 7 days.")


# ---------------------------------------------------------------------
# Shared exam rendering
# ---------------------------------------------------------------------

def render_exam_row(exam: dict):
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 2, 1])
        with c1:
            st.markdown(f"**{exam['title']}**")
            org = exam["organization"]["name"]
            state = exam["state"]["name"] if exam.get("state") else "Central"
            st.caption(f"{org} · {state}")
        with c2:
            st.markdown(status_pill(exam["status"]), unsafe_allow_html=True)
            if exam.get("application_end_date"):
                st.caption(f"Last date: {exam['application_end_date']}")
        with c3:
            if st.button("View", key=f"view_{exam['slug']}"):
                st.session_state.exam_slug = exam["slug"]
                st.session_state.view = "detail"
                st.rerun()


def render_exam_list(params: dict):
    status_filter = st.selectbox(
        "Status", ["All", "open", "closing_soon", "upcoming", "closed"], key="status_filter"
    )
    if status_filter != "All":
        params = {**params, "status": status_filter}

    exams = api_get("/exams", params)
    st.caption(f"{len(exams)} exam(s) found")
    if not exams:
        st.info("No exams match this filter yet.")
    for exam in exams:
        render_exam_row(exam)


# ---------------------------------------------------------------------
# ALL EXAMS view
# ---------------------------------------------------------------------

def render_all():
    st.subheader("📋 All Exams")
    render_exam_list({"scope": "all"})


# ---------------------------------------------------------------------
# STATE-WISE view
# ---------------------------------------------------------------------

def render_state():
    st.subheader("🗺️ State-wise")

    states = api_get("/states")

    if not st.session_state.state_slug:
        st.write("Select a state:")
        cols = st.columns(4)
        for i, state in enumerate(states):
            with cols[i % 4]:
                if st.button(state["name"], use_container_width=True, key=f"state_{state['slug']}"):
                    st.session_state.state_slug = state["slug"]
                    st.rerun()
        return

    state_name = next((s["name"] for s in states if s["slug"] == st.session_state.state_slug), "")
    left, right = st.columns([5, 1])
    with left:
        st.markdown(f"**Showing exams for: {state_name}**")
    with right:
        if st.button("Change state"):
            st.session_state.state_slug = None
            st.rerun()

    render_exam_list({"scope": "state", "state_slug": st.session_state.state_slug})


# ---------------------------------------------------------------------
# CENTRAL-WISE view
# ---------------------------------------------------------------------

def render_central():
    st.subheader("🇮🇳 Central-wise")

    orgs = api_get("/organizations", {"scope": "central"})

    if not st.session_state.org_slug:
        st.write("Select a central organization, or browse all central exams:")
        if st.button("All Central Exams", key="all_central"):
            st.session_state.org_slug = "__all__"
            st.rerun()
        cols = st.columns(4)
        for i, org in enumerate(orgs):
            with cols[i % 4]:
                if st.button(org["name"], use_container_width=True, key=f"org_{org['slug']}"):
                    st.session_state.org_slug = org["slug"]
                    st.rerun()
        return

    left, right = st.columns([5, 1])
    with left:
        if st.session_state.org_slug == "__all__":
            st.markdown("**Showing all central exams**")
        else:
            org_name = next((o["name"] for o in orgs if o["slug"] == st.session_state.org_slug), "")
            st.markdown(f"**Showing exams for: {org_name}**")
    with right:
        if st.button("Change org"):
            st.session_state.org_slug = None
            st.rerun()

    params = {"scope": "central"}
    if st.session_state.org_slug != "__all__":
        params["org_slug"] = st.session_state.org_slug
    render_exam_list(params)


# ---------------------------------------------------------------------
# EXAM DETAIL view
# ---------------------------------------------------------------------

def render_detail():
    exam = api_get(f"/exams/{st.session_state.exam_slug}")
    if not exam or isinstance(exam, list):
        st.error("Exam not found.")
        return

    st.subheader(exam["title"])
    st.markdown(status_pill(exam["status"]), unsafe_allow_html=True)
    if exam.get("is_verified"):
        st.caption(f"✅ Verified · last checked {exam.get('last_verified_at', 'n/a')}")
    else:
        st.caption("⚠️ Not yet verified against the official notification")

    st.write("")

    fact_sheet = {
        "Organization": exam["organization"]["name"],
        "Scope": "Central" if exam["organization"]["scope"] == "central" else "State",
        "State": exam["state"]["name"] if exam.get("state") else "—",
        "Category": ", ".join(c["name"] for c in exam.get("categories", [])) or "—",
        "Qualification": exam.get("qualification") or "—",
        "Age Limit": exam.get("age_limit") or "—",
        "Application Start Date": exam.get("application_start_date") or "—",
        "Last Date to Apply": exam.get("application_end_date") or "—",
        "Exam Date": exam.get("exam_date") or "—",
        "Application Fee": exam.get("application_fee") or "—",
        "Vacancies": exam.get("vacancies") or "—",
    }
    with st.container(border=True):
        for label, value in fact_sheet.items():
            c1, c2 = st.columns([1, 2])
            c1.markdown(f"**{label}**")
            c2.write(value)

    if exam.get("short_description"):
        st.write(exam["short_description"])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if exam.get("notification_pdf_url"):
            st.link_button("📄 View Official Notification", exam["notification_pdf_url"], use_container_width=True)
    with c2:
        if exam.get("apply_online_url"):
            st.link_button("🔗 Apply Online (Official Site)", exam["apply_online_url"], use_container_width=True, type="primary")

    st.caption(
        "UnifiedGov is an independent information portal, not affiliated with any "
        "government body. All applications must be submitted on the official website above."
    )


# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------

VIEWS = {
    "home": render_home,
    "all": render_all,
    "state": render_state,
    "central": render_central,
    "detail": render_detail,
}

VIEWS.get(st.session_state.view, render_home)()

st.divider()
st.caption("Not affiliated with any government body. · [About](#) · [Disclaimer](#) · [Contact](#)")
