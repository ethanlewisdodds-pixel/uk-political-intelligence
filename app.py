import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="UK Political Intelligence", layout="wide")
st.title("🇬🇧 UK Political Intelligence")
st.caption("Live monitoring of Parliament, Government & Commons activity")

# ─────────────────────────────────────────────────────────────
# POLICY AREAS
# ─────────────────────────────────────────────────────────────

POLICY_AREAS = [
    "Economy & Treasury",
    "Health & Social Care",
    "Education",
    "Home Affairs & Security",
    "Foreign Affairs & International Trade",
    "Defence",
    "Justice",
    "Environment & Rural Affairs",
    "Transport",
    "Housing & Planning",
    "Work & Pensions",
    "Business & Industry",
    "Science & Technology",
    "Culture, Media & Sport",
    "Energy & Net Zero",
]

POLICY_KEYWORDS = {
    "Economy & Treasury": ["tax", "finance", "budget", "treasury", "economic"],
    "Health & Social Care": ["health", "nhs", "social care", "mental health"],
    "Education": ["education", "school", "university", "skills"],
    "Home Affairs & Security": ["immigration", "police", "crime", "border"],
    "Foreign Affairs & International Trade": ["trade", "foreign", "sanctions"],
    "Defence": ["defence", "military", "armed forces"],
    "Justice": ["justice", "courts", "prison", "sentencing"],
    "Environment & Rural Affairs": ["environment", "farming", "nature"],
    "Transport": ["transport", "rail", "road", "aviation"],
    "Housing & Planning": ["housing", "planning", "rent"],
    "Work & Pensions": ["pension", "employment", "welfare"],
    "Business & Industry": ["business", "industry", "companies"],
    "Science & Technology": ["technology", "ai", "digital", "data"],
    "Culture, Media & Sport": ["culture", "media", "sport"],
    "Energy & Net Zero": ["energy", "climate", "net zero", "renewable"],
}

PARTY_COLOURS = {
    "Conservative": "#0087DC",
    "Labour": "#DC241F",
    "Liberal Democrat": "#FAA61A",
    "Scottish National Party": "#FFF95D",
    "Reform UK": "#12B6CF",
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def match_policy(text, keywords):
    text = text.lower()
    return any(k in text for k in keywords)

def format_date(date_str):
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except:
        return date_str[:10]

def days_remaining(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (dt.date() - datetime.now().date()).days
    except:
        return None

# ─────────────────────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_bills():
    url = "https://bills-api.parliament.uk/api/v1/Bills?CurrentHouse=All&IsDefeated=false&Take=200"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("items", [])
    except:
        pass
    return []

@st.cache_data(ttl=3600)
def fetch_consultations():
    url = (
        "https://www.gov.uk/api/search.json"
        "?filter_content_store_document_type=open_consultation"
        "&count=100"
        "&fields=title,link,description,public_timestamp,closing_date,organisations"
    )
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("results", [])
    except:
        pass
    return []

@st.cache_data(ttl=1800)
def fetch_hansard(policy):
    keywords = POLICY_KEYWORDS.get(policy, [])
    start = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    results = []
    for kw in keywords[:3]:
        url = (
            "https://hansard-api.parliament.uk/search.json"
            f"?query={kw}"
            f"&house=commons"
            f"&startDate={start}"
            f"&endDate={end}"
            "&take=15"
        )
        try:
            r = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
            if r.status_code == 200:
                results.extend(r.json().get("results", []))
        except:
            continue

    unique = {r["id"]: r for r in results if "id" in r}
    return list(unique.values())[:15]

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

st.sidebar.header("Policy Area")
selected_policy = st.sidebar.selectbox("Select area", POLICY_AREAS)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

keywords = POLICY_KEYWORDS[selected_policy]

# ─────────────────────────────────────────────────────────────
# FETCH DATA
# ─────────────────────────────────────────────────────────────

with st.spinner("Loading live data..."):
    bills = fetch_bills()
    consultations = fetch_consultations()
    debates = fetch_hansard(selected_policy)

# ─────────────────────────────────────────────────────────────
# FILTERED RESULTS
# ─────────────────────────────────────────────────────────────

filtered_bills = [
    b for b in bills
    if match_policy(
        (b.get("shortTitle","") + " " + b.get("longTitle","")), keywords
    )
]

filtered_consultations = []
for c in consultations:
    text = (c.get("title","") + " " + c.get("description","")).lower()
    score = sum(1 for k in keywords if k in text)
    if score > 0:
        c["score"] = score
        filtered_consultations.append(c)

filtered_consultations = sorted(filtered_consultations, key=lambda x: x["score"], reverse=True)

# ─────────────────────────────────────────────────────────────
# SUMMARY METRICS
# ─────────────────────────────────────────────────────────────

col1, col2, col3 = st.columns(3)
col1.metric("Active Bills", len(filtered_bills))
col2.metric("Open Consultations", len(filtered_consultations))
col3.metric("Commons Contributions (45d)", len(debates))

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# BILLS SECTION
# ─────────────────────────────────────────────────────────────

st.subheader("📋 Bills in Parliament")

for bill in sorted(filtered_bills, key=lambda x: x.get("lastUpdate",""), reverse=True):

    title = bill.get("shortTitle", "Untitled Bill")
    bill_id = bill.get("billId")
    stage = bill.get("currentStage", {}).get("description","Unknown stage")
    bill_type = bill.get("billType", {}).get("name","")
    sponsor = bill.get("sponsors", [{}])[0]
    sponsor_name = sponsor.get("member", {}).get("name","Unknown")
    sponsor_party = sponsor.get("member", {}).get("party","")

    badge_colour = "#C41E3A" if "Government" in bill_type else "#666666"
    badge = f"<span style='background:{badge_colour};color:white;padding:3px 8px;border-radius:8px;font-size:0.75em'>{bill_type}</span>"

    party_colour = PARTY_COLOURS.get(sponsor_party, "#888888")

    with st.expander(f"{title}"):
        st.markdown(badge, unsafe_allow_html=True)
        st.markdown(f"**Stage:** {stage}")
        st.markdown(f"**Sponsor:** <span style='color:{party_colour}'>{sponsor_name} ({sponsor_party})</span>", unsafe_allow_html=True)
        st.markdown(f"**Last Updated:** {format_date(bill.get('lastUpdate'))}")
        st.markdown(f"[View Bill](https://bills.parliament.uk/bills/{bill_id})")

# ─────────────────────────────────────────────────────────────
# CONSULTATIONS
# ─────────────────────────────────────────────────────────────

st.subheader("📣 Open Consultations")

for c in filtered_consultations[:20]:
    title = c.get("title")
    closing = c.get("closing_date", [{}])
    closing_date = closing[0].get("value","") if closing else ""
    days_left = days_remaining(closing_date)

    badge = ""
    if days_left is not None and days_left <= 14:
        badge = "<span style='background:#C41E3A;color:white;padding:3px 8px;border-radius:8px;font-size:0.75em'>Closing Soon</span>"

    with st.expander(title):
        if badge:
            st.markdown(badge, unsafe_allow_html=True)
        if closing_date:
            st.markdown(f"**Closes:** {format_date(closing_date)} ({days_left} days)")
        st.markdown(c.get("description",""))
        st.markdown(f"[Respond on GOV.UK](https://www.gov.uk{c.get('link')} )")

# ─────────────────────────────────────────────────────────────
# HANSARD
# ─────────────────────────────────────────────────────────────

st.subheader("🗣️ Recent Commons Contributions")

if debates:
    for d in debates:
        member = d.get("speaker","Unknown MP")
        date = d.get("date","")
        excerpt = d.get("excerpt","")

        with st.expander(f"{member} · {format_date(date)}"):
            st.markdown(excerpt)
else:
    st.info("No recent relevant contributions found.")
