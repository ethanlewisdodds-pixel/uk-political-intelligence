import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="UK Political Intelligence", layout="wide")
st.title("🇬🇧 UK Political Intelligence")
st.caption("Live data from the UK Parliament API")

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
    "Northern Ireland",
    "Scotland",
    "Wales",
    "Cabinet Office & Civil Service",
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

@st.cache_data(ttl=3600)
def fetch_bills():
    all_bills = []
    skip = 0
    take = 100
    session_start = "2024-07-04"
    while True:
        url = f"https://bills-api.parliament.uk/api/v1/Bills?CurrentHouse=All&IsDefeated=false&Skip={skip}&Take={take}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            break
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
        for bill in items:
            last_update = bill.get("lastUpdate", "")
            if last_update >= session_start:
                all_bills.append(bill)
        if len(all_bills) >= data.get("totalResults", 0):
            break
        skip += take

    # Deduplicate by billId, keeping the entry with the most recent lastUpdate
    seen = {}
    for bill in all_bills:
        bill_id = bill.get("billId")
        last_update = bill.get("lastUpdate", "")
        if bill_id not in seen or last_update > seen[bill_id].get("lastUpdate", ""):
            seen[bill_id] = bill

    return list(seen.values())

def match_policy(bill_title, keywords):
    title_lower = bill_title.lower()
    return any(kw in title_lower for kw in keywords)

def get_bill_stage_url(bill_id):
    return f"https://bills.parliament.uk/bills/{bill_id}"

# --- Sidebar ---
st.sidebar.header("Filter by Policy Area")
selected_policy = st.sidebar.selectbox("Select a policy area", POLICY_AREAS)

# --- Main content ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📋 Bills in Parliament — {selected_policy}")

    with st.spinner("Fetching live bills from Parliament..."):
        bills = fetch_bills()

    keywords = POLICY_BILL_KEYWORDS.get(selected_policy, [])
    filtered = [b for b in bills if match_policy(b.get("shortTitle", "") + " " + b.get("longTitle", ""), keywords)]

    if filtered:
        st.success(f"{len(filtered)} bill(s) found for this policy area")
        for bill in filtered:
            bill_id = bill.get("billId")
            title = bill.get("shortTitle", "Untitled Bill")
            stage = bill.get("currentStage", {})
            stage_name = stage.get("description", "Unknown stage") if isinstance(stage, dict) else "Unknown stage"
            house = bill.get("originatingHouse", "")
            bill_type = bill.get("billType", {}).get("name", "")
            url = get_bill_stage_url(bill_id)

            with st.expander(f"**{title}**"):
                st.markdown(f"**Current Stage:** {stage_name}")
                st.markdown(f"**Originating House:** {house}")
                st.markdown(f"**Bill Type:** {bill_type}")
                st.markdown(f"[🔗 View on Parliament website]({url})")
    else:
        st.info("No active bills found for this policy area. Try another, or this area may have no current legislation.")

with col2:
    st.subheader("ℹ️ About this app")
    st.markdown("""
    This app pulls **live data** from the UK Parliament API.
    
    **Currently showing:**
    - ✅ Active bills by policy area
    - ✅ Current parliamentary stage
    - ✅ Links to full bill details
    
    **Coming soon:**
    - 🔜 Ministers & key personnel
    - 🔜 Opposition spokespeople
    - 🔜 Open consultations
    - 🔜 Committee hearings
    - 🔜 Parliamentary questions
    """)
    st.markdown("---")
    st.markdown("Data refreshes every **hour** automatically.")
    if st.button("🔄 Refresh now"):
        st.cache_data.clear()
        st.rerun()
