import re
import time
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="UK Political Intelligence", layout="wide")

POLICY_KEYWORDS = {
    "Economy & Treasury": ["tax", "treasury", "finance", "budget", "fiscal"],
    "Health & Social Care": ["health", "nhs", "social care", "mental health"],
    "Education": ["education", "school", "university", "skills"],
    "Home Affairs & Security": ["home office", "immigration", "crime", "police", "security"],
    "Foreign Affairs & International Trade": ["foreign", "trade", "sanctions", "export", "import"],
    "Defence": ["defence", "armed forces", "military", "veterans"],
    "Justice": ["justice", "courts", "sentencing", "prisons"],
    "Environment & Rural Affairs": ["environment", "farming", "rural", "climate", "nature"],
    "Transport": ["transport", "rail", "road", "aviation", "bus"],
    "Housing & Planning": ["housing", "planning", "rent", "building"],
    "Work & Pensions": ["work", "pension", "benefits", "employment"],
    "Business & Industry": ["business", "industry", "consumer", "competition"],
    "Science & Technology": ["technology", "science", "ai", "digital", "data"],
    "Culture, Media & Sport": ["culture", "media", "sport", "arts"],
    "Energy & Net Zero": ["energy", "net zero", "renewable", "nuclear", "carbon"],
}

COMMITTEE_HINTS = {
    "Economy & Treasury": ["Treasury"],
    "Health & Social Care": ["Health and Social Care"],
    "Education": ["Education"],
    "Home Affairs & Security": ["Home Affairs"],
    "Foreign Affairs & International Trade": ["Foreign Affairs", "Business and Trade"],
    "Defence": ["Defence"],
    "Justice": ["Justice"],
    "Environment & Rural Affairs": ["Environment", "Rural Affairs"],
    "Transport": ["Transport"],
    "Housing & Planning": ["Housing"],
    "Work & Pensions": ["Work and Pensions"],
    "Business & Industry": ["Business and Trade"],
    "Science & Technology": ["Science, Innovation and Technology"],
    "Culture, Media & Sport": ["Culture, Media and Sport"],
    "Energy & Net Zero": ["Energy Security and Net Zero"],
}


def normalise_bill_title(bill: dict) -> str:
    title = bill.get("shortTitle") or bill.get("title") or ""
    return re.sub(r"\s+", " ", title.strip().lower())


def classify_policy(text: str) -> str:
    content = (text or "").lower()
    for policy, keywords in POLICY_KEYWORDS.items():
        if any(keyword in content for keyword in keywords):
            return policy
    return "Other"


@st.cache_data(ttl=900)
def fetch_bills() -> list[dict]:
    all_bills, skip, take = [], 0, 100
    while True:
        url = f"https://bills-api.parliament.uk/api/v1/Bills?CurrentHouse=All&IsDefeated=false&Skip={skip}&Take={take}"
        try:
            response = requests.get(url, timeout=12)
            if response.status_code != 200:
                break
            data = response.json()
        except Exception:
            break
        items = data.get("items", [])
        if not items:
            break
        all_bills.extend(items)
        skip += take
        if skip >= data.get("totalResults", 0):
            break

    seen = {}
    for bill in all_bills:
        bill_id = bill.get("billId")
        if not bill_id:
            continue
        if bill_id not in seen or bill.get("lastUpdate", "") > seen[bill_id].get("lastUpdate", ""):
            seen[bill_id] = bill

    dedup = {}
    for bill in seen.values():
        stage = (bill.get("currentStage") or {}).get("description", "")
        if bill.get("isAct") or "royal assent" in stage.lower():
            continue
        key = normalise_bill_title(bill) or str(bill.get("billId"))
        if key not in dedup or bill.get("lastUpdate", "") > dedup[key].get("lastUpdate", ""):
            dedup[key] = bill
    return list(dedup.values())


@st.cache_data(ttl=1800)
def fetch_consultations() -> list[dict]:
    url = (
        "https://www.gov.uk/api/search.json"
        "?filter_content_store_document_type=open_consultation"
        "&count=200"
        "&fields=title,link,description,public_timestamp,closing_date,organisations"
    )
    try:
        r = requests.get(url, timeout=12)
        return r.json().get("results", []) if r.status_code == 200 else []
    except Exception:
        return []


@st.cache_data(ttl=900)
def fetch_hansard() -> list[dict]:
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    terms = ["tax", "nhs", "education", "immigration", "defence", "housing", "energy", "technology"]
    contributions = []
    for term in terms:
        url = (
            "https://hansard.parliament.uk/search/Contributions"
            f"?searchTerm={requests.utils.quote(term)}&startDate={start_date}&endDate={end_date}"
            "&house=Commons&take=12&outputType=2"
        )
        try:
            r = requests.get(url, timeout=12)
            if r.status_code == 200:
                contributions.extend(r.json().get("Contributions", []))
        except Exception:
            continue

    unique = {}
    for item in contributions:
        ext_id = item.get("ContributionExtId")
        if ext_id and ext_id not in unique:
            unique[ext_id] = item
    return list(unique.values())


@st.cache_data(ttl=3600)
def fetch_committees() -> list[dict]:
    all_committees, skip, take = [], 0, 40
    while True:
        url = f"https://committees-api.parliament.uk/api/Committees?house=Commons&CurrentlyActive=true&skip={skip}&take={take}"
        try:
            r = requests.get(url, timeout=12)
            if r.status_code != 200:
                break
            data = r.json()
        except Exception:
            break
        items = data.get("items", [])
        if not items:
            break
        all_committees.extend(items)
        skip += take
        if skip >= data.get("totalResults", 0):
            break
    return all_committees


def to_date(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except Exception:
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except Exception:
            return None


def score_priority(days_to_close: int | None, stage: str) -> int:
    score = 1
    if days_to_close is not None:
        if days_to_close <= 7:
            score += 3
        elif days_to_close <= 21:
            score += 2
    if "committee" in (stage or "").lower():
        score += 2
    elif "report" in (stage or "").lower():
        score += 1
    return min(score, 5)


st.title("🇬🇧 UK Political Intelligence Command Centre")
st.caption("Integrated monitoring of UK legislation, consultations, parliamentary debate and committee activity.")

with st.sidebar:
    st.header("Control Centre")
    refresh_sec = st.slider("Auto-refresh (seconds)", 0, 600, 120, step=30)
    selected_policies = st.multiselect(
        "Track policy areas",
        options=list(POLICY_KEYWORDS.keys()),
        default=["Economy & Treasury", "Health & Social Care", "Energy & Net Zero"],
    )
    watchlist = st.text_area("Watchlist keywords (comma-separated)", "inflation, net zero, migration")

if not selected_policies:
    st.warning("Choose at least one policy area to load intelligence.")
    st.stop()

with st.spinner("Collecting live parliamentary and government data..."):
    bills = fetch_bills()
    consultations = fetch_consultations()
    hansard = fetch_hansard()
    committees = fetch_committees()

policy_set = set(selected_policies)
watch_terms = [w.strip().lower() for w in watchlist.split(",") if w.strip()]

bill_rows = []
for b in bills:
    title = b.get("shortTitle") or b.get("title") or "Untitled bill"
    policy = classify_policy(title)
    if policy not in policy_set:
        continue
    stage = (b.get("currentStage") or {}).get("description", "Unknown")
    bill_rows.append(
        {
            "Policy": policy,
            "Title": title,
            "Stage": stage,
            "Updated": to_date(b.get("lastUpdate", "")),
            "URL": f"https://bills.parliament.uk/bills/{b.get('billId')}",
            "Watchlist Hit": any(term in title.lower() for term in watch_terms),
        }
    )

consult_rows = []
for c in consultations:
    title = c.get("title", "")
    description = c.get("description", "")
    combined = f"{title} {description}"
    policy = classify_policy(combined)
    if policy not in policy_set:
        continue
    close_raw = (c.get("closing_date") or [{}])[0].get("value", "") if c.get("closing_date") else ""
    close_date = to_date(close_raw)
    days_to_close = (close_date - datetime.now().date()).days if close_date else None
    consult_rows.append(
        {
            "Policy": policy,
            "Title": title,
            "Closing Date": close_date,
            "Days to Close": days_to_close,
            "Priority": score_priority(days_to_close, ""),
            "URL": f"https://www.gov.uk{c.get('link', '')}",
            "Watchlist Hit": any(term in combined.lower() for term in watch_terms),
        }
    )

hansard_rows = []
for h in hansard:
    section = h.get("DebateSection", "")
    text = re.sub("<.*?>", " ", h.get("Value", ""))
    combined = f"{section} {text}"
    policy = classify_policy(combined)
    if policy not in policy_set:
        continue
    hansard_rows.append(
        {
            "Policy": policy,
            "Member": h.get("AttributedTo", "Unknown"),
            "Debate": section or "General debate",
            "Date": to_date(h.get("SittingDate", "")),
            "Excerpt": text[:220],
            "Watchlist Hit": any(term in combined.lower() for term in watch_terms),
        }
    )

committee_rows = []
for c in committees:
    name = c.get("name", "")
    matched = [p for p in policy_set if any(hint.lower() in name.lower() for hint in COMMITTEE_HINTS.get(p, []))]
    for policy in matched:
        committee_rows.append(
            {
                "Policy": policy,
                "Committee": name,
                "Contact": (c.get("contact") or {}).get("email", ""),
                "URL": f"https://committees.parliament.uk/committee/{c.get('id')}/",
            }
        )

bills_df = pd.DataFrame(bill_rows)
consult_df = pd.DataFrame(consult_rows)
hansard_df = pd.DataFrame(hansard_rows)
committee_df = pd.DataFrame(committee_rows)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Active Bills", len(bills_df))
col2.metric("Open Consultations", len(consult_df))
col3.metric("Hansard Contributions", len(hansard_df))
col4.metric("Relevant Committees", len(committee_df))
watch_hits = sum(df.get("Watchlist Hit", pd.Series(dtype=bool)).sum() for df in [bills_df, consult_df, hansard_df])
col5.metric("Watchlist Alerts", int(watch_hits))

alerts = []
if not consult_df.empty:
    urgent = consult_df[consult_df["Days to Close"].fillna(999) <= 7]
    if not urgent.empty:
        alerts.append(f"{len(urgent)} consultation(s) closing within 7 days.")
if not bills_df.empty:
    committee_stage = bills_df[bills_df["Stage"].str.contains("committee", case=False, na=False)]
    if not committee_stage.empty:
        alerts.append(f"{len(committee_stage)} bill(s) currently at Committee stage.")
if alerts:
    st.warning(" | ".join(alerts))

tab1, tab2, tab3, tab4 = st.tabs(["Executive Dashboard", "Legislation", "Consultations", "Parliament Activity"])

with tab1:
    left, right = st.columns(2)
    with left:
        if not bills_df.empty:
            stage_counts = bills_df.groupby(["Stage", "Policy"]).size().reset_index(name="Count")
            chart = alt.Chart(stage_counts).mark_bar().encode(
                x=alt.X("Stage:N", sort='-y'),
                y="Count:Q",
                color="Policy:N",
                tooltip=["Policy", "Stage", "Count"],
            ).properties(title="Bills by Stage")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No bill data for selected policy areas.")
    with right:
        if not consult_df.empty and consult_df["Closing Date"].notna().any():
            close_df = consult_df.dropna(subset=["Closing Date"])
            chart = alt.Chart(close_df).mark_circle().encode(
                x="Closing Date:T",
                y="Policy:N",
                size="Priority:Q",
                color=alt.Color("Days to Close:Q", scale=alt.Scale(scheme="redyellowgreen", reverse=True)),
                tooltip=["Title", "Policy", "Days to Close", "Priority"],
            ).properties(title="Consultation Deadline Radar")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No consultation deadlines available.")

with tab2:
    st.subheader("Legislation Monitor")
    if not bills_df.empty:
        recent_days = st.slider("Show bills updated in the last N days", 7, 180, 45)
        threshold = datetime.now().date() - timedelta(days=recent_days)
        filtered_bills = bills_df[bills_df["Updated"].fillna(datetime(1970, 1, 1).date()) >= threshold]
        st.dataframe(filtered_bills[["Policy", "Title", "Stage", "Updated", "Watchlist Hit", "URL"]], use_container_width=True)
        st.download_button("Download bills CSV", filtered_bills.to_csv(index=False), "bills_monitor.csv", "text/csv")
    else:
        st.info("No active bills match your selected policy areas.")

with tab3:
    st.subheader("Consultation Response Planner")
    if not consult_df.empty:
        st.dataframe(
            consult_df.sort_values(by="Days to Close", na_position="last")[["Policy", "Title", "Closing Date", "Days to Close", "Priority", "Watchlist Hit", "URL"]],
            use_container_width=True,
        )
        st.download_button("Download consultations CSV", consult_df.to_csv(index=False), "consultations_monitor.csv", "text/csv")
    else:
        st.info("No open consultations match current filters.")

with tab4:
    top, bottom = st.columns(2)
    with top:
        st.subheader("Hansard Activity Stream")
        if not hansard_df.empty:
            trend = hansard_df.dropna(subset=["Date"]).groupby(["Date", "Policy"]).size().reset_index(name="Contributions")
            chart = alt.Chart(trend).mark_bar().encode(
                x="Date:T",
                y="Contributions:Q",
                color="Policy:N",
                tooltip=["Date", "Policy", "Contributions"],
            ).properties(title="Contributions over time")
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(hansard_df[["Policy", "Date", "Member", "Debate", "Excerpt", "Watchlist Hit"]], use_container_width=True)
        else:
            st.info("No Hansard contributions for selected policy areas.")
    with bottom:
        st.subheader("Committee Directory")
        if not committee_df.empty:
            st.dataframe(committee_df[["Policy", "Committee", "Contact", "URL"]], use_container_width=True)
        else:
            st.info("No committees mapped for current selection.")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: {'off' if refresh_sec == 0 else f'every {refresh_sec}s'}")


if refresh_sec:
    time.sleep(refresh_sec)
    st.rerun()
