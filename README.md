# Saint Rocco's KPI Dashboard

A Streamlit dashboard for exploring financial KPIs, scenario modeling, and budget vs actual analysis.

## Quick Start (3 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the dashboard
```bash
streamlit run dashboard.py
```

### 3. Open in browser
Streamlit will automatically open `http://localhost:8501`

---

## What's inside

| Tab | Contents |
|-----|----------|
| 📊 Performance | FY2024 vs FY2025 KPI scorecards, annual revenue & profitability bars, margin comparison |
| 📈 Revenue Trends | Monthly channel breakdown, margin trends, EBITDA bars, cash balance, channel mix pie |
| 🎛️ Scenario Model | Real-time P&L based on sidebar inputs, EBITDA waterfall, sensitivity heat map |
| 📋 Budget vs Actual | Feb-26 BvA table, actual vs budget bars, variance chart |

## Scenario Sliders (left sidebar)

Adjust any of these to update the Scenario tab in real time:

- **DTC Revenue Growth %** — YoY growth rate for DTC channel
- **Wholesale Revenue Growth %** — YoY wholesale growth
- **Paid Marketing Spend ($K)** — annual paid ad budget
- **Gross Margin Target %** — blended gross margin
- **Fulfillment % of Net Rev** — warehouse + shipping costs
- **Month-1 Retention Rate %** — repeat purchase rate at 1 month
- **DTC AOV ($)** — average order value for new customers
- **Active Wholesale Accounts** — end-of-year account target
- **Annual Events** — total events driving organic acquisition

---

## Connecting to live data

The dashboard currently uses hardcoded data extracted from `StR_Financial_Model_2026-03-24.xlsx`.

To make it live, replace the data block at the top of `dashboard.py` with a loader:

```python
import pandas as pd

@st.cache_data(ttl=3600)  # refresh hourly
def load_data():
    # Option A: Read from Excel file
    df = pd.read_excel("StR_Financial_Model_2026-03-24.xlsx",
                       sheet_name="O.KPIs", header=None)
    return df

# Option B: Read from Google Sheets (requires gspread)
# import gspread
# gc = gspread.service_account(filename='credentials.json')
# sh = gc.open_by_url('your-sheet-url')
```

---

## Deploying to Streamlit Cloud (free)

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo — it will auto-detect `dashboard.py`
4. Share the public URL with your team

No server setup, no licensing, no cost.
