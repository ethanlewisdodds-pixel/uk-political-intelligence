# UK Political Intelligence

A Streamlit command centre for monitoring UK political activity across:
- Active legislation (UK Parliament Bills API)
- Open consultations (GOV.UK search API)
- Recent Commons contributions (Hansard)
- Relevant Commons select committees

## Key features

- **Multi-policy monitoring** with side-by-side comparisons
- **Auto-refresh controls** for near real-time tracking
- **Executive KPI strip** (bills, consultations, Hansard contributions, committees, watchlist alerts)
- **Integrated visualisations**:
  - Bills by stage
  - Consultation deadline radar
  - Hansard contributions over time
- **Watchlist intelligence** using user-defined keywords
- **Urgency indicators** for consultations and committee-stage bills
- **Operational tables + CSV export** for downstream workflows

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app defaults to tracking high-priority policy domains, and can be adjusted from the sidebar.
