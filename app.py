import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="UK Political Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── DESIGN SYSTEM ─────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400;1,700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --navy:        #0d1b2a;
    --navy-mid:    #162236;
    --navy-light:  #1e3352;
    --gold:        #c9a84c;
    --gold-light:  #e8cc82;
    --gold-pale:   #f5efd0;
    --cream:       #f7f3ec;
    --cream-dark:  #ece7dd;
    --ink:         #1c1c2e;
    --ink-mid:     #3d3d5c;
    --ink-faint:   #7a7a99;
    --red-govt:    #8b1a1a;
    --tory:        #0087DC;
    --reform:      #12B6CF;
    --libdem:      #FAA61A;
    --stage-done:  #c9a84c;
    --stage-curr:  #0d1b2a;
    --stage-todo:  #ddd8cf;
    --shadow-sm:   0 1px 4px rgba(13,27,42,0.08);
    --shadow-md:   0 4px 16px rgba(13,27,42,0.12);
    --shadow-lg:   0 8px 32px rgba(13,27,42,0.18);
}

/* ─── RESET & GLOBAL ─── */
html, body, [class*="css"] { font-family: 'Crimson Pro', Georgia, serif; }
.stApp { background: var(--cream); }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 3px solid var(--gold) !important;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--gold) !important;
    color: var(--navy) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--navy-mid) !important;
    border-color: var(--navy-light) !important;
    color: var(--cream) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span { color: var(--cream) !important; }

/* ─── STREAMLIT COMPONENT OVERRIDES ─── */
[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid var(--cream-dark) !important;
    border-radius: 6px !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 0.5rem !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Crimson Pro', serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: var(--navy) !important;
    padding: 0.85rem 1.25rem !important;
}
.stSpinner > div { border-top-color: var(--gold) !important; }
.stSuccess { background: var(--gold-pale) !important; border-color: var(--gold) !important; }
.stInfo { background: #e8f0f8 !important; }

/* ─── TITLE BANNER ─── */
.title-banner {
    background: var(--navy);
    background-image: repeating-linear-gradient(
        90deg, transparent, transparent 60px,
        rgba(201,168,76,0.04) 60px, rgba(201,168,76,0.04) 61px
    );
    margin: -1rem -1rem 0 -1rem;
    padding: 2rem 2.5rem 1.75rem;
    border-bottom: 3px solid var(--gold);
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.title-crown {
    font-size: 3rem;
    line-height: 1;
    opacity: 0.9;
    flex-shrink: 0;
}
.title-text h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.9rem !important;
    font-weight: 900 !important;
    color: white !important;
    margin: 0 !important;
    padding: 0 !important;
    letter-spacing: -0.01em;
    line-height: 1.1;
}
.title-text .subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--gold);
    margin-top: 0.4rem;
}
.title-right {
    margin-left: auto;
    text-align: right;
}
.title-date {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: var(--gold-light);
    font-size: 0.95rem;
}
.title-session {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: rgba(201,168,76,0.6);
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* ─── SECTION HEADERS ─── */
.section-hd {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 2.25rem 0 1.25rem 0;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--cream-dark);
    position: relative;
}
.section-hd::before {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 60px;
    height: 2px;
    background: var(--gold);
}
.section-icon {
    width: 34px; height: 34px;
    background: var(--navy);
    color: var(--gold);
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
}
.section-hd h3 {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    margin: 0 !important; padding: 0 !important;
}
.section-meta {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-faint);
}

/* ─── DIVIDER ─── */
.gold-rule {
    height: 1px;
    background: linear-gradient(90deg, var(--gold) 0%, transparent 100%);
    opacity: 0.25;
    margin: 2rem 0;
}

/* ─── COUNT PILL ─── */
.count-pill {
    display: inline-block;
    background: var(--navy);
    color: var(--gold);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 2px;
    margin-bottom: 1rem;
}
.empty-notice {
    background: var(--cream-dark);
    border-radius: 6px;
    padding: 1.5rem 2rem;
    font-family: 'Crimson Pro', serif;
    font-style: italic;
    color: var(--ink-faint);
    font-size: 1rem;
    text-align: center;
}

/* ─── PERSONNEL ─── */
.person-col-hd {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding-bottom: 0.5rem;
    margin-bottom: 0.85rem;
    border-bottom: 2px solid;
}
.person-col-hd.gov { color: var(--red-govt); border-color: var(--red-govt); }
.person-col-hd.opp { color: var(--navy); border-color: var(--navy); }

.person-row {
    background: white;
    border-radius: 5px;
    padding: 0.7rem 0.9rem 0.7rem 1rem;
    margin-bottom: 0.5rem;
    box-shadow: var(--shadow-sm);
    border-left: 3px solid var(--cream-dark);
    transition: border-color 0.15s, transform 0.15s;
}
.person-row:hover { transform: translateX(2px); }
.person-row.cabinet  { border-left-color: var(--red-govt); }
.person-row.minister { border-left-color: #c0392b; }
.person-row.civil    { border-left-color: var(--navy-light); }
.person-row.tory     { border-left-color: var(--tory); }
.person-row.reform   { border-left-color: var(--reform); }
.person-row.libdem   { border-left-color: var(--libdem); }

.person-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 1px 6px;
    border-radius: 2px;
    color: white;
    margin-bottom: 0.25rem;
}
.pb-cabinet  { background: var(--red-govt); }
.pb-minister { background: #c0392b; }
.pb-civil    { background: var(--navy-light); }
.pb-tory     { background: var(--tory); }
.pb-reform   { background: var(--reform); }
.pb-libdem   { background: var(--libdem); color: var(--navy) !important; }
.person-name { font-family: 'Crimson Pro', serif; font-weight: 600; font-size: 1rem; color: var(--ink); }
.person-role { font-family: 'Crimson Pro', serif; font-size: 0.88rem; color: var(--ink-faint); font-style: italic; margin-top: 0.1rem; }

/* ─── BILL CARDS ─── */
.bill-card {
    background: white;
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-md);
    border-top: 3px solid var(--navy);
    position: relative;
    overflow: hidden;
}
.bill-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 80px; height: 80px;
    background: radial-gradient(circle at top right, rgba(201,168,76,0.07), transparent 70%);
    pointer-events: none;
}
.bill-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 0.5rem;
    line-height: 1.3;
}
.bill-meta-row {
    display: flex; gap: 1.5rem; flex-wrap: wrap;
    margin-bottom: 1.1rem;
}
.bill-meta-item {
    font-family: 'Crimson Pro', serif;
    font-size: 0.88rem;
    color: var(--ink-faint);
}
.bill-meta-item strong { color: var(--ink-mid); font-weight: 600; }

/* ─── BILL PIPELINE TRACKER ─── */
.pipeline-wrap {
    margin: 0.5rem 0 0.75rem;
    padding: 1rem 0.5rem 0.75rem;
    background: var(--cream);
    border-radius: 6px;
}
.pipeline-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 0.6rem;
    padding-left: 0.25rem;
}
.pipeline-track {
    display: flex;
    align-items: flex-start;
    position: relative;
    padding: 0 0.5rem;
}
.pip-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
    z-index: 1;
}
.pip-item:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 9px;
    left: calc(50% + 9px);
    width: calc(100% - 18px);
    height: 2px;
    background: var(--stage-todo);
    z-index: 0;
}
.pip-item.done:not(:last-child)::after { background: var(--stage-done); }
.pip-dot {
    width: 20px; height: 20px;
    border-radius: 50%;
    background: var(--stage-todo);
    border: 2px solid var(--stage-todo);
    position: relative; z-index: 1; flex-shrink: 0;
    transition: background 0.2s;
}
.pip-item.done .pip-dot {
    background: var(--stage-done);
    border-color: var(--stage-done);
}
.pip-item.curr .pip-dot {
    background: var(--stage-curr);
    border-color: var(--stage-curr);
    box-shadow: 0 0 0 3px rgba(13,27,42,0.12), 0 0 0 5px rgba(201,168,76,0.2);
}
.pip-label {
    font-family: 'Crimson Pro', serif;
    font-size: 0.68rem;
    text-align: center;
    margin-top: 0.35rem;
    color: var(--ink-faint);
    line-height: 1.2;
    max-width: 52px;
}
.pip-item.done .pip-label { color: var(--ink-mid); font-weight: 600; }
.pip-item.curr .pip-label { color: var(--navy); font-weight: 700; }

.curr-stage-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--navy);
    color: var(--gold);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    padding: 4px 12px 4px 10px;
    border-radius: 20px;
    margin-top: 0.8rem;
}
.curr-stage-tag::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--gold);
    flex-shrink: 0;
}
.days-ago-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--cream-dark);
    color: var(--ink-mid);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.04em;
    padding: 4px 10px;
    border-radius: 20px;
    margin-top: 0.8rem;
    margin-left: 0.5rem;
}
.bill-link {
    display: inline-block;
    margin-top: 0.85rem;
    font-family: 'Crimson Pro', serif;
    font-size: 0.9rem;
    color: var(--navy);
    text-decoration: none;
    border-bottom: 1px solid var(--gold);
    padding-bottom: 1px;
    transition: color 0.15s, border-color 0.15s;
}
.bill-link:hover { color: var(--gold); }

/* ─── CONSULTATION CARDS ─── */
.consult-card {
    background: white;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow-sm);
    border-left: 4px solid var(--gold);
}
.consult-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.3rem;
    line-height: 1.3;
}
.consult-dept {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 0.5rem;
}
.consult-closes {
    display: inline-block;
    background: #fef9e7;
    border: 1px solid #f0c040;
    color: #7a5c00;
    font-family: 'Crimson Pro', serif;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 3px;
    margin-bottom: 0.6rem;
}
.consult-desc {
    font-family: 'Crimson Pro', serif;
    font-size: 0.95rem;
    color: var(--ink-mid);
    line-height: 1.55;
    margin-bottom: 0.5rem;
}

/* ─── HANSARD CARDS ─── */
.hansard-card {
    background: white;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow-sm);
    border-left: 4px solid var(--navy-light);
    position: relative;
}
.hansard-card::before {
    content: '\201C';
    position: absolute;
    top: 0.5rem; right: 1rem;
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    color: var(--cream-dark);
    line-height: 1;
    pointer-events: none;
}
.hansard-member {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700;
    color: var(--navy); margin-bottom: 0.15rem;
}
.hansard-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 0.6rem;
}
.hansard-text {
    font-family: 'Crimson Pro', serif;
    font-style: italic;
    font-size: 0.97rem;
    color: var(--ink-mid);
    line-height: 1.6;
    margin-bottom: 0.5rem;
}

/* ─── COMMITTEE CARDS ─── */
.committee-card {
    background: white;
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.6rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    border-top: 2px solid var(--cream-dark);
    transition: border-top-color 0.2s;
}
.committee-card:hover { border-top-color: var(--gold); }
.committee-name {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700;
    color: var(--navy); margin-bottom: 0.3rem;
}
.committee-contact {
    font-family: 'Crimson Pro', serif;
    font-size: 0.87rem;
    color: var(--ink-faint);
    line-height: 1.5;
}
.committee-btn {
    display: inline-block;
    background: var(--navy);
    color: var(--gold) !important;
    font-family: 'Crimson Pro', serif;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 7px 16px;
    border-radius: 4px;
    text-decoration: none !important;
    white-space: nowrap;
    flex-shrink: 0;
    transition: background 0.15s;
}
.committee-btn:hover { background: var(--navy-light); }

/* ─── FOOTER ─── */
.app-footer {
    margin-top: 3rem;
    padding: 1.25rem 1.75rem;
    background: var(--navy);
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 2px solid var(--gold);
}
.footer-brand {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: var(--gold-light);
    font-size: 0.95rem;
}
.footer-sources {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(201,168,76,0.5);
}
</style>
""", unsafe_allow_html=True)


# ── CONSTANTS ─────────────────────────────────────────────────────

POLICY_AREAS = [
    "Economy & Treasury", "Health & Social Care", "Education",
    "Home Affairs & Security", "Foreign Affairs & International Trade",
    "Defence", "Justice", "Environment & Rural Affairs", "Transport",
    "Housing & Planning", "Work & Pensions", "Business & Industry",
    "Science & Technology", "Culture, Media & Sport", "Energy & Net Zero",
    "Northern Ireland", "Scotland", "Wales", "Cabinet Office & Civil Service",
]

POLICY_BILL_KEYWORDS = {
    "Economy & Treasury": ["finance", "tax", "budget", "economic", "treasury", "fiscal", "national insurance", "stamp duty"],
    "Health & Social Care": ["health", "nhs", "mental health", "social care", "medicine", "pharmaceutical", "patient"],
    "Education": ["education", "school", "university", "children", "apprenticeship", "skills", "ofsted"],
    "Home Affairs & Security": ["immigration", "asylum", "police", "crime", "counter-terrorism", "border", "nationality"],
    "Foreign Affairs & International Trade": ["trade", "foreign", "sanctions", "treaty", "diplomatic", "export", "import"],
    "Defence": ["defence", "armed forces", "military", "veterans", "navy", "army", "air force"],
    "Justice": ["justice", "courts", "sentencing", "legal aid", "prisons", "probation", "offender"],
    "Environment & Rural Affairs": ["environment", "agriculture", "farming", "animal", "nature", "biodiversity", "flood", "rural"],
    "Transport": ["transport", "rail", "road", "aviation", "bus", "cycling", "driving", "vehicle"],
    "Housing & Planning": ["housing", "planning", "renters", "leasehold", "building", "property"],
    "Work & Pensions": ["pension", "employment", "disability", "welfare", "universal credit", "labour market"],
    "Business & Industry": ["business", "companies", "competition", "consumer", "industry", "retail", "startup"],
    "Science & Technology": ["science", "technology", "digital", "ai", "artificial intelligence", "data", "cyber", "innovation"],
    "Culture, Media & Sport": ["culture", "media", "sport", "broadcasting", "arts", "heritage", "gambling", "tourism"],
    "Energy & Net Zero": ["energy", "net zero", "climate", "renewable", "nuclear", "oil", "gas", "carbon"],
    "Northern Ireland": ["northern ireland"],
    "Scotland": ["scotland"],
    "Wales": ["wales"],
    "Cabinet Office & Civil Service": ["civil service", "cabinet office", "government reform", "procurement", "public sector"],
}

CONSULTATION_KEYWORDS = {
    "Economy & Treasury": ["tax", "finance", "treasury", "fiscal", "economic", "budget", "national insurance"],
    "Health & Social Care": ["health", "nhs", "social care", "medicine", "patient", "mental health"],
    "Education": ["education", "school", "university", "skills", "children", "apprenticeship"],
    "Home Affairs & Security": ["immigration", "police", "crime", "border", "asylum", "security", "counter-terrorism"],
    "Foreign Affairs & International Trade": ["trade", "export", "import", "sanctions", "foreign"],
    "Defence": ["defence", "military", "armed forces", "veterans"],
    "Justice": ["justice", "courts", "prison", "sentencing", "legal", "probation"],
    "Environment & Rural Affairs": ["environment", "farming", "agriculture", "nature", "biodiversity", "animal", "rural", "flood"],
    "Transport": ["transport", "rail", "road", "aviation", "bus", "vehicle", "driving"],
    "Housing & Planning": ["housing", "planning", "renters", "building", "leasehold", "property"],
    "Work & Pensions": ["pension", "employment", "welfare", "disability", "universal credit"],
    "Business & Industry": ["business", "industry", "competition", "consumer", "companies"],
    "Science & Technology": ["technology", "digital", "ai", "data", "cyber", "science", "innovation"],
    "Culture, Media & Sport": ["culture", "media", "sport", "broadcasting", "arts", "gambling", "heritage"],
    "Energy & Net Zero": ["energy", "net zero", "climate", "renewable", "nuclear", "carbon", "oil", "gas"],
    "Northern Ireland": ["northern ireland"],
    "Scotland": ["scotland"],
    "Wales": ["wales"],
    "Cabinet Office & Civil Service": ["civil service", "cabinet office", "public sector", "procurement"],
}

CONSULTATION_DEPARTMENTS = {
    "Economy & Treasury": ["treasury", "hmrc", "revenue", "customs"],
    "Health & Social Care": ["health", "social care", "dhsc"],
    "Education": ["education", "dfe"],
    "Home Affairs & Security": ["home office", "home affairs", "border"],
    "Foreign Affairs & International Trade": ["foreign", "fcdo", "trade", "export"],
    "Defence": ["defence", "mod", "ministry of defence"],
    "Justice": ["justice", "attorney", "legal"],
    "Environment & Rural Affairs": ["environment", "rural", "defra", "food"],
    "Transport": ["transport", "dft", "highways", "maritime"],
    "Housing & Planning": ["housing", "communities", "local government", "planning", "mhclg"],
    "Work & Pensions": ["work", "pensions", "dwp"],
    "Business & Industry": ["business", "trade", "dbt", "industry"],
    "Science & Technology": ["science", "technology", "innovation", "dsit", "digital"],
    "Culture, Media & Sport": ["culture", "media", "sport", "dcms", "gambling"],
    "Energy & Net Zero": ["energy", "net zero", "desnz", "climate"],
    "Northern Ireland": ["northern ireland"],
    "Scotland": ["scotland office", "scottish"],
    "Wales": ["wales office", "welsh"],
    "Cabinet Office & Civil Service": ["cabinet office", "civil service"],
}

QUESTION_KEYWORDS = {
    "Economy & Treasury": ["tax", "finance", "treasury", "budget", "economic", "fiscal", "national insurance", "spending", "borrowing", "debt"],
    "Health & Social Care": ["health", "nhs", "hospital", "social care", "mental health", "medicine", "patient", "gp", "dentist", "ambulance"],
    "Education": ["education", "school", "university", "teacher", "pupil", "apprenticeship", "ofsted", "curriculum"],
    "Home Affairs & Security": ["immigration", "asylum", "police", "crime", "border", "visa", "deportation", "security"],
    "Foreign Affairs & International Trade": ["trade", "foreign", "sanctions", "diplomatic", "export", "import", "aid"],
    "Defence": ["defence", "military", "army", "navy", "air force", "veterans", "armed forces"],
    "Justice": ["justice", "courts", "prison", "sentencing", "legal aid", "probation", "reoffending"],
    "Environment & Rural Affairs": ["environment", "farming", "agriculture", "nature", "flood", "animal welfare", "rural", "biodiversity"],
    "Transport": ["transport", "rail", "railway", "road", "aviation", "bus", "cycling", "vehicle", "traffic"],
    "Housing & Planning": ["housing", "planning", "renters", "leasehold", "building", "property", "landlord", "tenant"],
    "Work & Pensions": ["pension", "employment", "welfare", "disability", "universal credit", "jobcentre"],
    "Business & Industry": ["business", "industry", "competition", "consumer", "companies", "startup", "retail"],
    "Science & Technology": ["technology", "digital", "artificial intelligence", "ai", "data", "cyber", "science", "innovation"],
    "Culture, Media & Sport": ["culture", "media", "sport", "broadcasting", "arts", "gambling", "heritage", "tourism"],
    "Energy & Net Zero": ["energy", "net zero", "climate", "renewable", "nuclear", "carbon", "oil", "gas", "electricity"],
    "Northern Ireland": ["northern ireland"],
    "Scotland": ["scotland"],
    "Wales": ["wales"],
    "Cabinet Office & Civil Service": ["civil service", "cabinet office", "public sector", "procurement", "government reform"],
}

COMMITTEE_MAP = {
    "Economy & Treasury": ["Treasury", "Public Accounts"],
    "Health & Social Care": ["Health and Social Care"],
    "Education": ["Education"],
    "Home Affairs & Security": ["Home Affairs"],
    "Foreign Affairs & International Trade": ["Foreign Affairs", "International Trade"],
    "Defence": ["Defence"],
    "Justice": ["Justice"],
    "Environment & Rural Affairs": ["Environment, Food and Rural Affairs"],
    "Transport": ["Transport"],
    "Housing & Planning": ["Housing, Communities and Local Government"],
    "Work & Pensions": ["Work and Pensions"],
    "Business & Industry": ["Business and Trade"],
    "Science & Technology": ["Science, Innovation and Technology"],
    "Culture, Media & Sport": ["Culture, Media and Sport"],
    "Energy & Net Zero": ["Energy Security and Net Zero"],
    "Northern Ireland": ["Northern Ireland Affairs"],
    "Scotland": ["Scottish Affairs"],
    "Wales": ["Welsh Affairs"],
    "Cabinet Office & Civil Service": ["Public Administration and Constitutional Affairs"],
}

PERSONNEL = {
    "Economy & Treasury": {
        "government": [
            {"name": "Rachel Reeves MP", "role": "Chancellor of the Exchequer", "type": "Cabinet Minister"},
            {"name": "Darren Jones MP", "role": "Chief Secretary to the Treasury", "type": "Cabinet Minister"},
            {"name": "James Murray MP", "role": "Exchequer Secretary to the Treasury", "type": "Minister"},
            {"name": "Tulip Siddiq MP", "role": "Economic Secretary to the Treasury", "type": "Minister"},
            {"name": "Emma Reynolds MP", "role": "Financial Secretary to the Treasury", "type": "Minister"},
            {"name": "James Bowler", "role": "Permanent Secretary, HM Treasury", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Mel Stride MP", "role": "Shadow Chancellor", "party": "Conservative"},
            {"name": "Richard Fuller MP", "role": "Shadow Chief Secretary to the Treasury", "party": "Conservative"},
            {"name": "Nigel Farage MP", "role": "Leader / Economy Spokesperson", "party": "Reform UK"},
            {"name": "Sarah Olney MP", "role": "Treasury Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Health & Social Care": {
        "government": [
            {"name": "Wes Streeting MP", "role": "Secretary of State for Health & Social Care", "type": "Cabinet Minister"},
            {"name": "Karin Smyth MP", "role": "Minister of State for Health", "type": "Minister"},
            {"name": "Stephen Kinnock MP", "role": "Minister of State for Social Care", "type": "Minister"},
            {"name": "Andrew Gwynne MP", "role": "Parliamentary Under Secretary (Public Health)", "type": "Minister"},
            {"name": "Sir Chris Wormald", "role": "Permanent Secretary, DHSC", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Edward Argar MP", "role": "Shadow Secretary of State for Health", "party": "Conservative"},
            {"name": "Richard Tice", "role": "Health Spokesperson", "party": "Reform UK"},
            {"name": "Helen Morgan MP", "role": "Health & Social Care Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Education": {
        "government": [
            {"name": "Bridget Phillipson MP", "role": "Secretary of State for Education", "type": "Cabinet Minister"},
            {"name": "Jacqui Smith", "role": "Minister of State for Education (Lords)", "type": "Minister"},
            {"name": "Janet Daby MP", "role": "Parliamentary Under Secretary (Children)", "type": "Minister"},
            {"name": "Susan Acland-Hood", "role": "Permanent Secretary, DfE", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Laura Trott MP", "role": "Shadow Secretary of State for Education", "party": "Conservative"},
            {"name": "Reform UK", "role": "Education Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Munira Wilson MP", "role": "Education Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Home Affairs & Security": {
        "government": [
            {"name": "Yvette Cooper MP", "role": "Secretary of State for the Home Department", "type": "Cabinet Minister"},
            {"name": "Dan Jarvis MP", "role": "Minister of State for Security", "type": "Minister"},
            {"name": "Seema Malhotra MP", "role": "Parliamentary Under Secretary (Migration)", "type": "Minister"},
            {"name": "Jess Phillips MP", "role": "Parliamentary Under Secretary (Safeguarding)", "type": "Minister"},
            {"name": "Sir Matthew Rycroft", "role": "Permanent Secretary, Home Office", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "James Cleverly MP", "role": "Shadow Home Secretary", "party": "Conservative"},
            {"name": "Lee Anderson MP", "role": "Home Affairs Spokesperson", "party": "Reform UK"},
            {"name": "Alistair Carmichael MP", "role": "Home Affairs Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Foreign Affairs & International Trade": {
        "government": [
            {"name": "David Lammy MP", "role": "Secretary of State for Foreign Affairs", "type": "Cabinet Minister"},
            {"name": "Douglas Alexander MP", "role": "Minister of State (Trade)", "type": "Minister"},
            {"name": "Stephen Doughty MP", "role": "Minister of State (Europe)", "type": "Minister"},
            {"name": "Sir Philip Barton", "role": "Permanent Secretary, FCDO", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Priti Patel MP", "role": "Shadow Foreign Secretary", "party": "Conservative"},
            {"name": "Ben Habib", "role": "Foreign Affairs Spokesperson", "party": "Reform UK"},
            {"name": "Calum Miller MP", "role": "Foreign Affairs Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Defence": {
        "government": [
            {"name": "John Healey MP", "role": "Secretary of State for Defence", "type": "Cabinet Minister"},
            {"name": "Luke Pollard MP", "role": "Minister of State for the Armed Forces", "type": "Minister"},
            {"name": "Maria Eagle MP", "role": "Minister of State for Defence Procurement", "type": "Minister"},
            {"name": "David Williams", "role": "Permanent Secretary, MoD", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "James Cartlidge MP", "role": "Shadow Defence Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Defence Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Richard Foord MP", "role": "Defence Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Justice": {
        "government": [
            {"name": "Shabana Mahmood MP", "role": "Lord Chancellor & Secretary of State for Justice", "type": "Cabinet Minister"},
            {"name": "Heidi Alexander MP", "role": "Minister of State for Courts", "type": "Minister"},
            {"name": "Lord Timpson", "role": "Minister of State for Prisons", "type": "Minister"},
            {"name": "Antonia Romeo", "role": "Permanent Secretary, MoJ", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Robert Jenrick MP", "role": "Shadow Justice Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Justice Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Josh Babarinde MP", "role": "Justice Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Environment & Rural Affairs": {
        "government": [
            {"name": "Steve Reed MP", "role": "Secretary of State for Environment, Food & Rural Affairs", "type": "Cabinet Minister"},
            {"name": "Mary Creagh MP", "role": "Parliamentary Under Secretary (Nature)", "type": "Minister"},
            {"name": "Daniel Zeichner MP", "role": "Minister of State for Food & Farming", "type": "Minister"},
            {"name": "Tamara Finkelstein", "role": "Permanent Secretary, Defra", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Victoria Atkins MP", "role": "Shadow Environment Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Environment Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Tim Farron MP", "role": "Environment & Rural Affairs Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Transport": {
        "government": [
            {"name": "Heidi Alexander MP", "role": "Secretary of State for Transport", "type": "Cabinet Minister"},
            {"name": "Mike Kane MP", "role": "Minister of State for Aviation", "type": "Minister"},
            {"name": "Simon Lightwood MP", "role": "Parliamentary Under Secretary (Rail)", "type": "Minister"},
            {"name": "Bernadette Kelly", "role": "Permanent Secretary, DfT", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Gareth Bacon MP", "role": "Shadow Transport Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Transport Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Wera Hobhouse MP", "role": "Transport Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Housing & Planning": {
        "government": [
            {"name": "Angela Rayner MP", "role": "Deputy PM & Secretary of State for Housing, Communities & Local Government", "type": "Cabinet Minister"},
            {"name": "Matthew Pennycook MP", "role": "Minister of State for Housing", "type": "Minister"},
            {"name": "Jim McMahon MP", "role": "Minister of State for Local Government", "type": "Minister"},
            {"name": "Sarah Healey", "role": "Permanent Secretary, MHCLG", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Kevin Hollinrake MP", "role": "Shadow Housing Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Housing Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Gideon Amos MP", "role": "Housing & Planning Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Work & Pensions": {
        "government": [
            {"name": "Liz Kendall MP", "role": "Secretary of State for Work & Pensions", "type": "Cabinet Minister"},
            {"name": "Alison McGovern MP", "role": "Minister of State for Employment", "type": "Minister"},
            {"name": "Sir Peter Schofield", "role": "Permanent Secretary, DWP", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Helen Whately MP", "role": "Shadow Work & Pensions Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Work & Pensions Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Steve Darling MP", "role": "Work & Pensions Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Business & Industry": {
        "government": [
            {"name": "Jonathan Reynolds MP", "role": "Secretary of State for Business & Trade", "type": "Cabinet Minister"},
            {"name": "Sarah Jones MP", "role": "Minister of State for Industry", "type": "Minister"},
            {"name": "Justin Madders MP", "role": "Parliamentary Under Secretary (Employment Rights)", "type": "Minister"},
            {"name": "Gareth Thomas MP", "role": "Parliamentary Under Secretary (Trade)", "type": "Minister"},
            {"name": "Dame Bernadette Kelly", "role": "Permanent Secretary, DBT", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Andrew Griffith MP", "role": "Shadow Business & Trade Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Business Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Daisy Cooper MP", "role": "Business Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Science & Technology": {
        "government": [
            {"name": "Peter Kyle MP", "role": "Secretary of State for Science, Innovation & Technology", "type": "Cabinet Minister"},
            {"name": "Feryal Clark MP", "role": "Parliamentary Under Secretary (AI & Digital)", "type": "Minister"},
            {"name": "Lord Vallance", "role": "Minister of State for Science", "type": "Minister"},
            {"name": "Sarah Munby", "role": "Permanent Secretary, DSIT", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Alan Mak MP", "role": "Shadow Science & Technology Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Science & Technology Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Victoria Collins MP", "role": "Science & Technology Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Culture, Media & Sport": {
        "government": [
            {"name": "Lisa Nandy MP", "role": "Secretary of State for Culture, Media & Sport", "type": "Cabinet Minister"},
            {"name": "Chris Bryant MP", "role": "Minister of State for Media & Creative Industries", "type": "Minister"},
            {"name": "Stephanie Peacock MP", "role": "Parliamentary Under Secretary (Sport)", "type": "Minister"},
            {"name": "Dame Sarah Healey", "role": "Permanent Secretary, DCMS", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Julia Lopez MP", "role": "Shadow Culture Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Culture Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Max Wilkinson MP", "role": "Culture, Media & Sport Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Energy & Net Zero": {
        "government": [
            {"name": "Ed Miliband MP", "role": "Secretary of State for Energy Security & Net Zero", "type": "Cabinet Minister"},
            {"name": "Michael Shanks MP", "role": "Parliamentary Under Secretary (Energy)", "type": "Minister"},
            {"name": "Lord Hunt of Kings Heath", "role": "Minister of State for Energy in Lords", "type": "Minister"},
            {"name": "Jeremy Pocklington", "role": "Permanent Secretary, DESNZ", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Claire Coutinho MP", "role": "Shadow Energy Secretary", "party": "Conservative"},
            {"name": "Nigel Farage MP", "role": "Net Zero Critic / Party Leader", "party": "Reform UK"},
            {"name": "Pippa Heylings MP", "role": "Energy & Climate Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Northern Ireland": {
        "government": [
            {"name": "Hilary Benn MP", "role": "Secretary of State for Northern Ireland", "type": "Cabinet Minister"},
            {"name": "Fleur Anderson MP", "role": "Parliamentary Under Secretary", "type": "Minister"},
            {"name": "Madeleine Alessandri", "role": "Permanent Secretary, NIO", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Alex Davies-Jones MP", "role": "Shadow NI Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "NI Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Alistair Carmichael MP", "role": "NI Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Scotland": {
        "government": [
            {"name": "Ian Murray MP", "role": "Secretary of State for Scotland", "type": "Cabinet Minister"},
            {"name": "Kirsty McNeill MP", "role": "Parliamentary Under Secretary", "type": "Minister"},
            {"name": "Joanna Crellin", "role": "Permanent Secretary, Scotland Office", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "John Lamont MP", "role": "Shadow Scotland Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Scotland Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Christine Jardine MP", "role": "Scotland Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Wales": {
        "government": [
            {"name": "Jo Stevens MP", "role": "Secretary of State for Wales", "type": "Cabinet Minister"},
            {"name": "Sir Wyn Williams", "role": "Permanent Secretary, Wales Office", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Alun Cairns MP", "role": "Shadow Wales Secretary", "party": "Conservative"},
            {"name": "Reform UK", "role": "Wales Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "David Chadwick MP", "role": "Wales Spokesperson", "party": "Liberal Democrats"},
        ],
    },
    "Cabinet Office & Civil Service": {
        "government": [
            {"name": "Pat McFadden MP", "role": "Chancellor of the Duchy of Lancaster", "type": "Cabinet Minister"},
            {"name": "Nick Thomas-Symonds MP", "role": "Minister for the Cabinet Office", "type": "Minister"},
            {"name": "Georgia Gould MP", "role": "Parliamentary Secretary, Cabinet Office", "type": "Minister"},
            {"name": "Cat Little", "role": "Cabinet Secretary & Head of the Civil Service", "type": "Civil Servant"},
        ],
        "opposition": [
            {"name": "Alex Burghart MP", "role": "Shadow Cabinet Office Minister", "party": "Conservative"},
            {"name": "Reform UK", "role": "Cabinet Office Spokesperson (TBC)", "party": "Reform UK"},
            {"name": "Alistair Carmichael MP", "role": "Cabinet Office Spokesperson", "party": "Liberal Democrats"},
        ],
    },
}

# ── BILL PIPELINE ─────────────────────────────────────────────────

# Each tuple: (short label, keywords to match against stage description)
BILL_STAGES = [
    ("1st Reading",    ["1st reading", "first reading"]),
    ("2nd Reading",    ["2nd reading", "second reading"]),
    ("Committee",      ["committee stage", "committee"]),
    ("Report",         ["report stage"]),
    ("3rd Reading",    ["3rd reading", "third reading"]),
    ("Lords 1st",      ["1st reading (lords)", "lords: 1st", "lords first reading"]),
    ("Lords 2nd",      ["2nd reading (lords)", "lords: 2nd", "lords second reading"]),
    ("Lords Cmte",     ["lords committee", "committee stage (lords)"]),
    ("Lords Report",   ["lords report", "report stage (lords)"]),
    ("Lords 3rd",      ["3rd reading (lords)", "lords: 3rd", "lords third reading"]),
    ("Ping Pong",      ["ping pong", "consideration of amendments"]),
]

def stage_index(stage_name: str) -> int:
    s = stage_name.lower()
    for i, (_, keywords) in enumerate(BILL_STAGES):
        if any(k in s for k in keywords):
            return i
    return -1

def bill_pipeline_html(stage_name: str) -> str:
    curr = stage_index(stage_name)
    items = ""
    for i, (label, _) in enumerate(BILL_STAGES):
        if i < curr:
            cls = "done"
        elif i == curr:
            cls = "curr"
        else:
            cls = ""
        items += f'<div class="pip-item {cls}"><div class="pip-dot"></div><div class="pip-label">{label}</div></div>'

    # Days since last update is shown separately by the caller
    return f"""
    <div class="pipeline-wrap">
        <div class="pipeline-label">Parliamentary Progress</div>
        <div class="pipeline-track">{items}</div>
    </div>"""

# ── DATA FETCHING ─────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_bills():
    all_bills, skip, take, session_start = [], 0, 100, "2024-07-04"
    while True:
        r = requests.get(
            f"https://bills-api.parliament.uk/api/v1/Bills?CurrentHouse=All&IsDefeated=false&Skip={skip}&Take={take}",
            timeout=10)
        if r.status_code != 200:
            break
        data = r.json()
        items = data.get("items", [])
        if not items:
            break
        all_bills += [b for b in items if b.get("lastUpdate", "") >= session_start]
        if skip + take >= data.get("totalResults", 0):
            break
        skip += take
    seen = {}
    for b in all_bills:
        bid = b.get("billId")
        if bid not in seen or b.get("lastUpdate","") > seen[bid].get("lastUpdate",""):
            seen[bid] = b
    active = []
    for b in seen.values():
        s = b.get("currentStage", {})
        sname = s.get("description", "") if isinstance(s, dict) else ""
        if "royal assent" not in sname.lower() and not b.get("isAct", False):
            active.append(b)
    return active

@st.cache_data(ttl=3600)
def fetch_consultations():
    try:
        url = (
            "https://www.gov.uk/api/search.json"
            "?filter_content_store_document_type=open_consultation"
            "&count=100"
            "&fields=title,link,description,public_timestamp,closing_date,organisations"
        )

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()
        results = data.get("results", [])

        consultations = []

        for item in results:
            consultations.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "description": item.get("description", ""),
                "published": item.get("public_timestamp", ""),
                "closing_date": item.get("closing_date", ""),
                "organisations": item.get("organisations", []),
            })

        return consultations

    except Exception as e:
        st.error(f"Consultation fetch error: {e}")
        return []

@st.cache_data(ttl=1800)
def fetch_hansard_debates(policy_area):
    keywords = QUESTION_KEYWORDS.get(policy_area, [])
    if not keywords:
        return []
    all_d = []
    for kw in keywords[:2]:
        try:
            r = requests.get(
                f"https://hansard.parliament.uk/search/Contributions"
                f"?searchTerm={requests.utils.quote(kw)}"
                f"&startDate={(datetime.now()-timedelta(days=30)).strftime('%Y-%m-%d')}"
                f"&endDate={datetime.now().strftime('%Y-%m-%d')}"
                f"&house=Commons&take=10&outputType=2",
                timeout=10)
            if r.status_code == 200:
                all_d += r.json().get("Contributions", [])
        except Exception:
            continue
    seen = {}
    for d in all_d:
        did = d.get("ContributionExtId", "")
        if did and did not in seen:
            seen[did] = d
    return sorted(seen.values(), key=lambda x: x.get("SittingDate",""), reverse=True)[:15]

@st.cache_data(ttl=3600)
def fetch_committees():
    all_c, skip, take = [], 0, 30
    while True:
        try:
            r = requests.get(
                f"https://committees-api.parliament.uk/api/Committees?house=Commons&CurrentlyActive=true&skip={skip}&take={take}",
                timeout=10)
            if r.status_code != 200:
                break
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            all_c += items
            if len(all_c) >= data.get("totalResults", 0):
                break
            skip += take
        except Exception:
            break
    return all_c

# ── HELPERS ───────────────────────────────────────────────────────

def match_kw(text, keywords):
    t = text.lower()
    return any(k in t for k in keywords)

def fmt_date(s):
    if not s:
        return "Unknown"
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00")).strftime("%-d %B %Y")
    except Exception:
        return s[:10]

def days_ago(s):
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00")).replace(tzinfo=None)
        n = (datetime.utcnow() - dt).days
        if n == 0: return "today"
        if n == 1: return "yesterday"
        return f"{n} days ago"
    except Exception:
        return ""

def get_str(f):
    return f.get("value","") if isinstance(f, dict) else (f or "")

def consult_matches(c, ckw, cdepts):
    orgs = c.get("organisations", [])
    org_text = " ".join(o.get("title","") for o in orgs).lower()
    return (match_kw(get_str(c.get("title","")) + " " + get_str(c.get("description","")), ckw)
            and any(d in org_text for d in cdepts))

def person_html(p, is_gov):
    if is_gov:
        t = p.get("type","Minister")
        row_cls = {"Cabinet Minister":"cabinet","Minister":"minister","Civil Servant":"civil"}.get(t,"minister")
        badge_cls = {"Cabinet Minister":"pb-cabinet","Minister":"pb-minister","Civil Servant":"pb-civil"}.get(t,"pb-minister")
        badge_txt = t
    else:
        party = p.get("party","")
        row_cls = {"Conservative":"tory","Reform UK":"reform","Liberal Democrats":"libdem"}.get(party,"minister")
        badge_cls = {"Conservative":"pb-tory","Reform UK":"pb-reform","Liberal Democrats":"pb-libdem"}.get(party,"pb-minister")
        badge_txt = party
    return f"""<div class="person-row {row_cls}">
      <span class="person-badge {badge_cls}">{badge_txt}</span>
      <div class="person-name">{p['name']}</div>
      <div class="person-role">{p['role']}</div>
    </div>"""

def section_hd(icon, title, meta=""):
    return f"""<div class="section-hd">
      <div class="section-icon">{icon}</div>
      <h3>{title}</h3>
      {"<div class='section-meta'>" + meta + "</div>" if meta else ""}
    </div>"""

# ── SIDEBAR ───────────────────────────────────────────────────────

st.sidebar.markdown("""
<div style="padding:1.5rem 0 0.5rem; text-align:center;">
  <div style="font-family:'Playfair Display',serif; color:#c9a84c; font-size:1.5rem; font-weight:900; letter-spacing:-0.01em;">⚜</div>
  <div style="font-family:'Playfair Display',serif; color:#e8cc82; font-size:1rem; font-weight:700; margin-top:0.25rem;">Political Intelligence</div>
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; letter-spacing:0.12em; color:rgba(201,168,76,0.5); text-transform:uppercase; margin-top:0.2rem;">United Kingdom</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""<div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.1em; text-transform:uppercase; color:#c9a84c; margin-bottom:0.5rem;">Policy Area</div>""", unsafe_allow_html=True)
selected_policy = st.sidebar.selectbox("", POLICY_AREAS, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="font-family:'Crimson Pro',serif; font-size:0.88rem; color:#8899aa; line-height:1.8;">
  <div style="color:#c9a84c; font-weight:600; margin-bottom:0.3rem; font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.08em; text-transform:uppercase;">Live Data Sources</div>
  UK Parliament Bills API<br>
  GOV.UK Consultations API<br>
  Hansard Contributions API<br>
  Parliament Committees API
</div>
<div style="margin-top:1rem; font-family:'JetBrains Mono',monospace; font-size:0.62rem; letter-spacing:0.06em; color:rgba(201,168,76,0.4); text-transform:uppercase;">
  Auto-refresh · 60 min
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
if st.sidebar.button("↻  Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ── TITLE BANNER ──────────────────────────────────────────────────

now = datetime.now()
st.markdown(f"""
<div class="title-banner">
  <div class="title-crown">⚜</div>
  <div class="title-text">
    <h1>UK Political Intelligence</h1>
    <div class="subtitle">Parliamentary Monitor &nbsp;·&nbsp; {selected_policy}</div>
  </div>
  <div class="title-right">
    <div class="title-date">{now.strftime("%-d %B %Y")}</div>
    <div class="title-session">Session 2024–25</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PERSONNEL ─────────────────────────────────────────────────────

st.markdown(section_hd("👥", f"Key People — {selected_policy}", "Ministers · Civil Servants · Opposition"), unsafe_allow_html=True)

personnel = PERSONNEL.get(selected_policy, {})
col_gov, col_opp = st.columns(2)
with col_gov:
    st.markdown('<div class="person-col-hd gov">🔴 &nbsp;Government</div>', unsafe_allow_html=True)
    for p in personnel.get("government", []):
        st.markdown(person_html(p, True), unsafe_allow_html=True)
with col_opp:
    st.markdown('<div class="person-col-hd opp">🔵 &nbsp;Opposition</div>', unsafe_allow_html=True)
    for p in personnel.get("opposition", []):
        st.markdown(person_html(p, False), unsafe_allow_html=True)

st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)

# ── BILLS ─────────────────────────────────────────────────────────

st.markdown(section_hd("📋", f"Bills in Parliament — {selected_policy}", "Current Session · Live from Parliament"), unsafe_allow_html=True)

with st.spinner("Loading bills…"):
    bills = fetch_bills()

bill_kw = POLICY_BILL_KEYWORDS.get(selected_policy, [])
filtered_bills = [b for b in bills if match_kw(b.get("shortTitle","") + " " + b.get("longTitle",""), bill_kw)]

if filtered_bills:
    st.markdown(f'<div class="count-pill">{len(filtered_bills)} active bill(s) found</div>', unsafe_allow_html=True)
    for bill in filtered_bills:
        bid       = bill.get("billId")
        title     = bill.get("shortTitle", "Untitled Bill")
        stage_obj = bill.get("currentStage", {})
        stage_name = stage_obj.get("description", "Unknown stage") if isinstance(stage_obj, dict) else "Unknown stage"
        house     = bill.get("originatingHouse", "Unknown")
        btype     = bill.get("billType", {}).get("name", "")
        last_upd  = bill.get("lastUpdate", "")
        url       = f"https://bills.parliament.uk/bills/{bid}"
        ago       = days_ago(last_upd)

        pipeline  = bill_pipeline_html(stage_name)

        st.markdown(f"""
        <div class="bill-card">
          <div class="bill-title">{title}</div>
          <div class="bill-meta-row">
            <div class="bill-meta-item"><strong>House:</strong> {house}</div>
            <div class="bill-meta-item"><strong>Type:</strong> {btype}</div>
            <div class="bill-meta-item"><strong>Updated:</strong> {fmt_date(last_upd)}</div>
          </div>
          {pipeline}
          <div style="display:flex; align-items:center; gap:0; flex-wrap:wrap;">
            <span class="curr-stage-tag">{stage_name}</span>
            {"<span class='days-ago-tag'>Updated " + ago + "</span>" if ago else ""}
          </div>
          <div><a href="{url}" target="_blank" class="bill-link">View full bill on Parliament website →</a></div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="empty-notice">No active bills found for this policy area in the current session.</div>', unsafe_allow_html=True)

st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)

# ── CONSULTATIONS ─────────────────────────────────────────────────

st.markdown(section_hd("📣", f"Open Consultations — {selected_policy}", "Live from GOV.UK"), unsafe_allow_html=True)

with st.spinner("Loading consultations…"):
    all_consults = fetch_consultations()

ckw    = CONSULTATION_KEYWORDS.get(selected_policy, [])
cdepts = CONSULTATION_DEPARTMENTS.get(selected_policy, [])
filtered_consults = [c for c in all_consults if consult_matches(c, ckw, cdepts)]

if filtered_consults:
    st.markdown(f'<div class="count-pill">{len(filtered_consults)} open consultation(s)</div>', unsafe_allow_html=True)
    for c in filtered_consults:
        title   = get_str(c.get("title")) or "Untitled"
        desc    = get_str(c.get("description")) or ""
        link    = "https://www.gov.uk" + c.get("link", "")
        closing = c.get("closing_date", [{}])
        cdate   = closing[0].get("value","") if closing else ""
        orgs    = c.get("organisations", [])
        org_str = ", ".join(o.get("title","") for o in orgs) if orgs else "Unknown department"
        closes_html = f'<div class="consult-closes">Closes: {fmt_date(cdate)}</div>' if cdate else ""

        st.markdown(f"""
        <div class="consult-card">
          <div class="consult-title">{title}</div>
          <div class="consult-dept">{org_str}</div>
          {closes_html}
          <div class="consult-desc">{desc[:300]}{"…" if len(desc)>300 else ""}</div>
          <a href="{link}" target="_blank" style="font-family:'Crimson Pro',serif; font-size:0.9rem; color:var(--navy); border-bottom:1px solid var(--gold); text-decoration:none; padding-bottom:1px;">
            Respond to this consultation on GOV.UK →
          </a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="empty-notice">No open consultations found for this policy area right now.</div>', unsafe_allow_html=True)

st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)

# ── HANSARD DEBATES ───────────────────────────────────────────────

st.markdown(section_hd("🗣️", f"Recent Hansard Debates — {selected_policy}", "House of Commons · Last 30 days"), unsafe_allow_html=True)

with st.spinner("Loading Hansard contributions…"):
    debates = fetch_hansard_debates(selected_policy)

if debates:
    st.markdown(f'<div class="count-pill">{len(debates)} contribution(s) found</div>', unsafe_allow_html=True)
    for d in debates:
        member  = d.get("AttributedTo", "Unknown MP")
        ddate   = fmt_date(d.get("SittingDate",""))
        dtitle  = d.get("DebateSection", "Unknown debate")
        text    = d.get("Value","")
        clean   = text.replace("<p>","").replace("</p>"," ").replace("<br>"," ").strip()
        hid     = d.get("ContributionExtId","")
        hurl    = f"https://hansard.parliament.uk/Commons/{d.get('SittingDate','')[:10]}/debates/{hid}" if hid else ""
        link_h  = f'<a href="{hurl}" target="_blank" style="font-family:\'Crimson Pro\',serif; font-size:0.88rem; color:var(--navy); border-bottom:1px solid var(--gold); text-decoration:none; padding-bottom:1px;">Read in Hansard →</a>' if hurl else ""

        st.markdown(f"""
        <div class="hansard-card">
          <div class="hansard-member">{member}</div>
          <div class="hansard-meta">{dtitle} &nbsp;·&nbsp; {ddate}</div>
          <div class="hansard-text">"{clean[:420]}{"…" if len(clean)>420 else ""}"</div>
          {link_h}
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="empty-notice">No recent Hansard contributions found for this policy area.</div>', unsafe_allow_html=True)

st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)

# ── SELECT COMMITTEES ─────────────────────────────────────────────

st.markdown(section_hd("🏛️", f"Select Committees — {selected_policy}", "House of Commons · Currently Active"), unsafe_allow_html=True)

with st.spinner("Loading committees…"):
    all_cmtes = fetch_committees()

rel_names = COMMITTEE_MAP.get(selected_policy, [])
matched   = [c for c in all_cmtes if any(n.lower() in c.get("name","").lower() for n in rel_names)]

if matched:
    for c in matched:
        name  = c.get("name","Unknown Committee")
        cid   = c.get("id")
        cont  = c.get("contact",{}) or {}
        phone = cont.get("phone","")
        email = cont.get("email","")
        curl  = f"https://committees.parliament.uk/committee/{cid}/" if cid else "https://committees.parliament.uk"
        contact_lines = []
        if email: contact_lines.append(f"✉ {email}")
        if phone: contact_lines.append(f"☎ {phone}")
        contact_str = "<br>".join(contact_lines) if contact_lines else "Contact via Parliament website"

        st.markdown(f"""
        <div class="committee-card">
          <div>
            <div class="committee-name">{name}</div>
            <div class="committee-contact">{contact_str}</div>
          </div>
          <a href="{curl}" target="_blank" class="committee-btn">View work &amp; inquiries →</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="empty-notice">Committee information not available for this policy area.</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────

st.markdown(f"""
<div class="app-footer">
  <div class="footer-brand">⚜ &nbsp;UK Political Intelligence Monitor</div>
  <div class="footer-sources">Parliament · GOV.UK · Hansard &nbsp;·&nbsp; {now.strftime("%-d %b %Y")}</div>
</div>
""", unsafe_allow_html=True)
