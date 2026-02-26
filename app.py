import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="UK Political Intelligence", layout="wide")
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(145deg, #f5f7fa 0%, #eef1f5 35%, #e4e9f0 100%);
            color: #1d2630;
        }
        .hero-banner {
            background: linear-gradient(120deg, #0b1f3a 0%, #16335c 45%, #1f4d7a 100%);
            color: #f8fbff;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 1.25rem 1.5rem;
            box-shadow: 0 10px 24px rgba(11, 31, 58, 0.18);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            color: #c3d4eb;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.75rem;
            margin-bottom: 0.15rem;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 650;
            margin: 0;
        }
        .hero-subtitle {
            margin-top: 0.35rem;
            color: #dae6f5;
            font-size: 0.95rem;
        }
        .section-note {
            color: #4b5d70;
            font-size: 0.88rem;
            margin-top: -0.35rem;
            margin-bottom: 0.6rem;
        }
        [data-testid="stMetricValue"] {
            color: #0b1f3a;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-kicker">United Kingdom Parliamentary Monitoring</div>
        <h1 class="hero-title">🇬🇧 UK Political Intelligence</h1>
        <div class="hero-subtitle">Live legislative, scrutiny, and consultation tracking powered by UK Parliament and GOV.UK data.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

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

PARTY_COLOURS = {
    "Conservative": "#0087DC",
    "Reform UK": "#12B6CF",
    "Liberal Democrats": "#FAA61A",
}

ROLE_COLOURS = {
    "Cabinet Minister": "#C41E3A",
    "Minister": "#E8927C",
    "Civil Servant": "#4A4A8A",
}

# ── DATA FETCHING ────────────────────────────────────────────────

def normalise_bill_title(bill):
    """Create a stable key so user-visible duplicate bills collapse reliably."""
    short_title = (bill.get("shortTitle") or "").strip()
    long_title = (bill.get("longTitle") or "").strip()
    base_title = short_title or long_title
    # Remove bracketed variants like [HL], [Lords], etc.
    base_title = re.sub(r"\[[^\]]+\]", "", base_title)
    # Keep only letters/numbers to avoid punctuation and apostrophe variants.
    base_title = re.sub(r"[^a-z0-9]", "", base_title.lower())
    return base_title


@st.cache_data(ttl=3600)
def fetch_bills():
    all_bills = []
    skip = 0
    take = 100
    session_start = "2024-07-04"
    while True:
        url = f"https://bills-api.parliament.uk/api/v1/Bills?CurrentHouse=All&IsDefeated=false&Skip={skip}&Take={take}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                break
            data = response.json()
        except Exception:
            break
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

    # Deduplicate by billId keeping most recent
    seen = {}
    for bill in all_bills:
        bill_id = bill.get("billId")
        last_update = bill.get("lastUpdate", "")
        if bill_id not in seen or last_update > seen[bill_id].get("lastUpdate", ""):
            seen[bill_id] = bill

    # Filter out bills that have already received Royal Assent or become Acts
    active = []
    for bill in seen.values():
        stage = bill.get("currentStage", {})
        stage_name = stage.get("description", "") if isinstance(stage, dict) else ""
        if "royal assent" not in stage_name.lower() and not bill.get("isAct", False):
            active.append(bill)

    # Secondary de-duplication: collapse user-visible duplicates by normalized
    # title and keep the most recently updated record.
    deduped_by_title = {}
    for bill in active:
        title_key = normalise_bill_title(bill)
        if not title_key:
            # Fall back to billId if title data is missing.
            title_key = f"bill-{bill.get('billId', '')}"
        last_update = bill.get("lastUpdate", "")
        if title_key not in deduped_by_title or last_update > deduped_by_title[title_key].get("lastUpdate", ""):
            deduped_by_title[title_key] = bill

    return list(deduped_by_title.values())

@st.cache_data(ttl=3600)
def fetch_consultations():
    url = (
        "https://www.gov.uk/api/search.json"
        "?filter_content_store_document_type=open_consultation"
        "&count=100"
        "&fields=title,link,description,public_timestamp,closing_date,organisations"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=1800)
def fetch_hansard_debates(policy_area):
    keywords = QUESTION_KEYWORDS.get(policy_area, [])
    if not keywords:
        return []
    all_debates = []
    for keyword in keywords[:2]:
        url = (
            f"https://hansard.parliament.uk/search/Contributions"
            f"?searchTerm={requests.utils.quote(keyword)}"
            f"&startDate={(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}"
            f"&endDate={datetime.now().strftime('%Y-%m-%d')}"
            f"&house=Commons"
            f"&take=10"
            f"&outputType=2"
        )
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                items = response.json().get("Contributions", [])
                all_debates.extend(items)
        except Exception:
            continue
    seen = {}
    for d in all_debates:
        did = d.get("ContributionExtId", "")
        if did and did not in seen:
            seen[did] = d
    results = list(seen.values())
    results.sort(key=lambda x: x.get("SittingDate", ""), reverse=True)
    return results[:15]

@st.cache_data(ttl=3600)
def fetch_committees():
    all_committees = []
    skip = 0
    take = 30
    while True:
        url = f"https://committees-api.parliament.uk/api/Committees?house=Commons&CurrentlyActive=true&skip={skip}&take={take}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                break
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            all_committees.extend(items)
            if len(all_committees) >= data.get("totalResults", 0):
                break
            skip += take
        except Exception:
            break
    return all_committees

# ── HELPERS ──────────────────────────────────────────────────────

def match_policy(text, keywords):
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

def format_date(date_str):
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%-d %B %Y")
    except Exception:
        return date_str[:10]


def parse_iso_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None


def estimate_next_sitting_day(from_date=None):
    base = from_date or datetime.utcnow()
    candidate = base + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate


def stage_progress_score(stage_name):
    stage_lower = (stage_name or "").lower()
    if "first reading" in stage_lower:
        return 15
    if "second reading" in stage_lower:
        return 30
    if "committee" in stage_lower:
        return 50
    if "report" in stage_lower:
        return 65
    if "third reading" in stage_lower:
        return 80
    if "consideration of amendments" in stage_lower or "ping pong" in stage_lower:
        return 90
    if "royal assent" in stage_lower:
        return 100
    return 20

def get_str(field):
    if isinstance(field, dict):
        return field.get("value", "")
    return field or ""

def get_bill_stage_url(bill_id):
    return f"https://bills.parliament.uk/bills/{bill_id}"

def consultation_matches(c, consult_keywords, consult_depts):
    orgs = c.get("organisations", [])
    org_text = " ".join([o.get("title", "") for o in orgs]).lower() if orgs else ""
    text_match = match_policy(
        get_str(c.get("title")) + " " + get_str(c.get("description")),
        consult_keywords
    )
    dept_match = any(dept in org_text for dept in consult_depts)
    return text_match and dept_match

# ── SIDEBAR ───────────────────────────────────────────────────────

st.sidebar.header("Filter by Policy Area")
selected_policy = st.sidebar.selectbox("Select a policy area", POLICY_AREAS)
st.sidebar.markdown("---")
st.sidebar.markdown("Data refreshes every **hour** automatically.")
if st.sidebar.button("🔄 Refresh now"):
    st.cache_data.clear()
    st.rerun()

# ── PERSONNEL ─────────────────────────────────────────────────────

st.subheader(f"👥 Key People — {selected_policy}")
personnel = PERSONNEL.get(selected_policy, {})
gov_col, opp_col = st.columns(2)

with gov_col:
    st.markdown("#### 🔴 Government")
    for person in personnel.get("government", []):
        colour = ROLE_COLOURS.get(person["type"], "#888888")
        badge = f'<span style="background-color:{colour};color:white;padding:2px 8px;border-radius:10px;font-size:0.75em">{person["type"]}</span>'
        st.markdown(f'{badge} **{person["name"]}**<br><span style="color:gray">{person["role"]}</span>', unsafe_allow_html=True)
        st.markdown("")

with opp_col:
    st.markdown("#### 🔵 Opposition")
    for person in personnel.get("opposition", []):
        colour = PARTY_COLOURS.get(person["party"], "#888888")
        badge = f'<span style="background-color:{colour};color:white;padding:2px 8px;border-radius:10px;font-size:0.75em">{person["party"]}</span>'
        st.markdown(f'{badge} **{person["name"]}**<br><span style="color:gray">{person["role"]}</span>', unsafe_allow_html=True)
        st.markdown("")

st.markdown("---")

# ── BILLS ─────────────────────────────────────────────────────────

st.subheader(f"📋 Bills in Parliament — {selected_policy}")
st.markdown("<div class='section-note'>Enhanced situational view: stage progression, update cadence, and likely next sitting day.</div>", unsafe_allow_html=True)
with st.spinner("Fetching live bills from Parliament..."):
    bills = fetch_bills()

bill_keywords = POLICY_BILL_KEYWORDS.get(selected_policy, [])
filtered_bills = [b for b in bills if match_policy(b.get("shortTitle", "") + " " + b.get("longTitle", ""), bill_keywords)]

if filtered_bills:
    st.success(f"{len(filtered_bills)} bill(s) found for this policy area")
    today_utc = datetime.utcnow()
    next_sitting = estimate_next_sitting_day(today_utc)
    days_until_next_sitting = (next_sitting.date() - today_utc.date()).days
    recent_activity = sorted(
        [parse_iso_date(b.get("lastUpdate", "")) for b in filtered_bills if parse_iso_date(b.get("lastUpdate", ""))],
        reverse=True,
    )
    freshest_update = recent_activity[0].strftime("%-d %B %Y") if recent_activity else "Unknown"

    bill_metrics = []
    for bill in filtered_bills:
        stage = bill.get("currentStage", {})
        stage_name = stage.get("description", "Unknown stage") if isinstance(stage, dict) else "Unknown stage"
        updated_at = parse_iso_date(bill.get("lastUpdate", ""))
        days_since_update = (today_utc.date() - updated_at.date()).days if updated_at else None
        bill_metrics.append(
            {
                "Bill": bill.get("shortTitle", "Untitled Bill"),
                "Stage": stage_name,
                "Progress": stage_progress_score(stage_name),
                "Days since update": days_since_update if days_since_update is not None else -1,
            }
        )

    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Active bills (policy area)", len(filtered_bills))
    metric_col_2.metric("Most recent bill update", freshest_update)
    metric_col_3.metric("Days until next likely sitting day", days_until_next_sitting)

    df_metrics = pd.DataFrame(bill_metrics)
    chart_col, table_col = st.columns([1.1, 1.3])
    with chart_col:
        st.caption("Estimated progress to Royal Assent (stage-weighted)")
        stage_chart = df_metrics[["Bill", "Progress"]].set_index("Bill").sort_values("Progress", ascending=False)
        st.bar_chart(stage_chart)
    with table_col:
        st.caption("Live bill monitoring table")
        display_df = df_metrics.copy()
        display_df["Days since update"] = display_df["Days since update"].replace(-1, "Unknown")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    for bill in filtered_bills:
        bill_id = bill.get("billId")
        title = bill.get("shortTitle", "Untitled Bill")
        stage = bill.get("currentStage", {})
        stage_name = stage.get("description", "Unknown stage") if isinstance(stage, dict) else "Unknown stage"
        house = bill.get("originatingHouse", "")
        bill_type = bill.get("billType", {}).get("name", "")
        parsed_update = parse_iso_date(bill.get("lastUpdate", ""))
        last_update = format_date(bill.get("lastUpdate", ""))
        days_since_update = (today_utc.date() - parsed_update.date()).days if parsed_update else None
        progress_value = stage_progress_score(stage_name)
        url = get_bill_stage_url(bill_id)
        with st.expander(f"**{title}**"):
            st.progress(progress_value / 100, text=f"Legislative progress estimate: {progress_value}%")
            st.markdown(f"**Current Stage:** {stage_name}")
            st.markdown(f"**Originating House:** {house}")
            st.markdown(f"**Bill Type:** {bill_type}")
            st.markdown(f"**Last Updated:** {last_update}")
            if days_since_update is not None:
                st.markdown(f"**Days Since Last Update:** {days_since_update}")
            st.markdown(f"[🔗 View full bill details on Parliament website]({url})")
else:
    st.info("No active bills found for this policy area.")

st.markdown("---")

# ── CONSULTATIONS ─────────────────────────────────────────────────

st.subheader(f"📣 Open Consultations — {selected_policy}")
with st.spinner("Fetching live consultations from GOV.UK..."):
    all_consultations = fetch_consultations()

consult_keywords = CONSULTATION_KEYWORDS.get(selected_policy, [])
consult_depts = CONSULTATION_DEPARTMENTS.get(selected_policy, [])
filtered_consultations = [c for c in all_consultations if consultation_matches(c, consult_keywords, consult_depts)]

if filtered_consultations:
    st.success(f"{len(filtered_consultations)} open consultation(s) found")
    for c in filtered_consultations:
        title = get_str(c.get("title")) or "Untitled"
        description = get_str(c.get("description")) or "No description available."
        link = "https://www.gov.uk" + c.get("link", "")
        closing = c.get("closing_date", [{}])
        closing_date = closing[0].get("value", "") if closing else ""
        orgs = c.get("organisations", [])
        org_names = ", ".join([o.get("title", "") for o in orgs]) if orgs else "Unknown department"
        with st.expander(f"**{title}**"):
            st.markdown(f"**Department:** {org_names}")
            if closing_date:
                st.markdown(f"**Closes:** {format_date(closing_date)}")
            st.markdown(description)
            st.markdown(f"[🔗 Respond to this consultation on GOV.UK]({link})")
else:
    st.info("No open consultations found for this policy area right now.")

st.markdown("---")

# ── HANSARD DEBATES ───────────────────────────────────────────────

st.subheader(f"🗣️ Recent Hansard Debates — {selected_policy}")
st.caption("Contributions in the House of Commons in the last 30 days")

with st.spinner("Fetching recent debates from Hansard..."):
    debates = fetch_hansard_debates(selected_policy)

if debates:
    st.success(f"{len(debates)} recent contribution(s) found")
    for d in debates:
        member = d.get("AttributedTo", "Unknown MP")
        date = format_date(d.get("SittingDate", ""))
        debate_title = d.get("DebateSection", "Unknown debate")
        text = d.get("Value", "")
        clean_text = text.replace("<p>", "").replace("</p>", " ").replace("<br>", " ")
        hansard_id = d.get("ContributionExtId", "")
        url = f"https://hansard.parliament.uk/Commons/{d.get('SittingDate', '')[:10]}/debates/{hansard_id}" if hansard_id else ""

        with st.expander(f"**{member}** · {debate_title} · {date}"):
            st.markdown(clean_text[:600] + ("..." if len(clean_text) > 600 else ""))
            if url:
                st.markdown(f"[🔗 Read full contribution in Hansard]({url})")
else:
    st.info("No recent Hansard contributions found for this policy area.")

st.markdown("---")

# ── SELECT COMMITTEES ─────────────────────────────────────────────

st.subheader(f"🏛️ Relevant Select Committees — {selected_policy}")
st.caption("House of Commons select committees scrutinising this policy area")

with st.spinner("Fetching committee information..."):
    all_committees = fetch_committees()

relevant_names = COMMITTEE_MAP.get(selected_policy, [])
matched_committees = [
    c for c in all_committees
    if any(name.lower() in c.get("name", "").lower() for name in relevant_names)
]

if matched_committees:
    for committee in matched_committees:
        name = committee.get("name", "Unknown Committee")
        committee_id = committee.get("id")
        contact = committee.get("contact", {}) or {}
        phone = contact.get("phone", "")
        email = contact.get("email", "")
        committee_url = f"https://committees.parliament.uk/committee/{committee_id}/" if committee_id else "https://committees.parliament.uk"

        with st.expander(f"**{name}**"):
            if phone:
                st.markdown(f"**Phone:** {phone}")
            if email:
                st.markdown(f"**Email:** {email}")
            st.markdown(f"[🔗 View committee work, inquiries & reports]({committee_url})")
else:
    st.info("Committee information not available for this policy area.")
