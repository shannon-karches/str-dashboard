import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Saint Rocco's  |  KPI Dashboard",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  /* Main background — deep navy */
  .stApp { background: #0d1b2a; }
  section[data-testid="stSidebar"] { background: #112236 !important; border-right: 1px solid #1c3450; }
  section[data-testid="stSidebar"] * { color: #d4c5a9 !important; }
  section[data-testid="stSidebar"] .stSlider label,
  section[data-testid="stSidebar"] .stSelectbox label { color: #9a8c78 !important; font-size: 12px !important; }

  /* KPI cards — navy with tan accents */
  .kpi-card {
    background: #112236;
    border: 1px solid #1c3450;
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
  }
  .kpi-card.navy::before  { background: #c9a84c; }
  .kpi-card.tan::before   { background: #c9a84c; }
  .kpi-card.green::before { background: #4caf7d; }
  .kpi-card.red::before   { background: #e05c5c; }
  .kpi-card.blue::before  { background: #c9a84c; }
  .kpi-card.teal::before  { background: #c9a84c; }
  .kpi-card.purple::before{ background: #c9a84c; }
  .kpi-card.indigo::before{ background: #c9a84c; }
  .kpi-card.rose::before  { background: #c9a84c; }
  .kpi-card.amber::before { background: #c9a84c; }
  .kpi-label  { color: #9a8c78; font-size: 11px; font-weight: 500; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 6px; }
  .kpi-value  { color: #f0e6d3; font-size: 26px; font-weight: 600; line-height: 1; margin-bottom: 6px; font-family: 'DM Mono', monospace; }
  .kpi-delta  { font-size: 12px; font-weight: 500; }
  .kpi-delta.pos { color: #4caf7d; }
  .kpi-delta.neg { color: #e05c5c; }
  .kpi-sub    { color: #9a8c78; font-size: 11px; margin-top: 2px; }

  /* Section headers */
  .section-header {
    color: #f0e6d3;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
    border-bottom: 1px solid #1c3450;
    padding-bottom: 10px;
    margin: 28px 0 16px;
  }

  /* Scenario banner */
  .scenario-banner {
    background: #112236;
    border: 1px solid #1c3450;
    border-left: 3px solid #c9a84c;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
    font-size: 13px;
    color: #9a8c78;
  }
  .scenario-banner strong { color: #f0e6d3; }

  /* BvA table */
  .bva-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .bva-table th {
    background: #1c3450; color: #9a8c78;
    font-size: 11px; font-weight: 500; letter-spacing: .05em;
    text-transform: uppercase; padding: 10px 14px; text-align: right;
    border-bottom: 1px solid #254a6e;
  }
  .bva-table th:first-child { text-align: left; }
  .bva-table td { padding: 9px 14px; border-bottom: 1px solid #152d45; color: #d4c5a9; text-align: right; }
  .bva-table td:first-child { text-align: left; color: #f0e6d3; font-weight: 500; }
  .bva-table tr:hover td { background: #162f4a; }
  .bva-table tr.section-row td { background: #1c3450; color: #9a8c78; font-size: 11px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; padding: 7px 14px; }
  .pos-var { color: #4caf7d !important; font-weight: 600; }
  .neg-var { color: #e05c5c !important; font-weight: 600; }

  /* Plotly chart background override */
  .js-plotly-plot .plotly { background: transparent !important; }

  /* Hide streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

LABELS = ['Jan-24','Feb-24','Mar-24','Apr-24','May-24','Jun-24',
          'Jul-24','Aug-24','Sep-24','Oct-24','Nov-24','Dec-24',
          'Jan-25','Feb-25','Mar-25','Apr-25','May-25','Jun-25',
          'Jul-25','Aug-25','Sep-25','Oct-25','Nov-25','Dec-25',
          'Jan-26','Feb-26','Mar-26','Apr-26','May-26','Jun-26',
          'Jul-26','Aug-26','Sep-26','Oct-26','Nov-26','Dec-26']

STATUS = (['Actuals']*26) + (['Forecast']*10)

GROSS_SALES = [79603.64,93686.18,124034.33,210971.28,296159.45,275984.77,294615.12,
               356673.62,366706.44,468244.16,576793.75,491335.28,542744.54,556555.15,
               694052.29,534988.63,562295.03,664745.66,659148.52,667698.17,669254.24,
               722869.2,822978.56,771519.35,584143.36,716329.51,
               917083.97,959753.72,1060694.14,1110161.78,1148580.22,
               1170100.74,1262873.78,1227427.11,1227427.11,1227427.11]

NET_REVENUE = [82076.75,89876.03,110178.06,212948.42,283842.42,260560.87,
               282046.65,337979.66,353258.52,441698.04,548861.4,463223.86,
               518524.78,525777.08,667019.85,514989.42,542165.58,639793.97,
               632693.69,641059.32,642183.63,693156.36,789001.82,739388.85,
               525777.08,657501.67,841645.47,881019.3,974163.85,1019557.79,
               1054620.35,1074660.48,1160100.0,1127290.0,1127290.0,1127290.0]

DTC_SALES = [71852.19,83652.04,102229.34,91259.46,113276.12,96479.62,
             103915.08,118095.26,115213.49,135803.33,145085.71,130453.27,
             124158.62,132198.28,144239.7,142243.14,153785.7,159019.83,
             148985.77,163753.82,157393.18,163050.53,192316.59,174361.14,
             174361.14,195003.5,
             220000,230000,245000,255000,265000,275000,285000,295000,295000,295000]

WHOLESALE_SALES = [0,0,10829.5,91145.75,127726.75,118021.9,141275.75,
                   176706.0,176706.0,238738.25,310723.75,252537.5,
                   289285.32,284655.57,388290.55,244609.77,255618.78,
                   340823.06,337682.37,340823.06,335397.38,380561.92,
                   448773.38,402162.0,236298.65,316831.15,
                   450000,470000,520000,545000,565000,570000,630000,610000,610000,610000]

EVENTS_SALES = [7751.45,10034.14,10975.49,12752.07,34411.58,47157.25,
                35436.29,43823.13,54761.28,59817.37,77033.41,64232.87,
                72337.28,84024.76,107037.82,97551.94,101148.84,119208.64,
                115453.37,107547.85,120152.87,120688.94,134049.28,
                147994.21,25327.57,36494.21,
                55000,60000,65000,70000,75000,80000,85000,90000,90000,90000]

DISTRIBUTOR_SALES = [0,0,0,15814,20745,14326,13988,18049.23,20025.67,
                     33885.21,43950.88,44111.64,56963.32,89402.34,
                     54484.22,50583.78,51741.71,45694.13,57026.98,
                     55573.44,56310.81,58567.81,48839.31,
                     47002.0,148156.0,168000.65,
                     192000,199000,230000,240000,250000,245000,262000,232000,232000,232000]

GROSS_MARGIN = [0.771,0.757,0.675,0.618,0.611,0.636,0.617,0.629,0.634,
                0.654,0.665,0.659,0.670,0.494,0.678,0.670,0.673,0.677,
                0.671,0.674,0.678,0.680,0.683,0.680,
                0.494,0.502,0.510,0.510,0.512,0.514,0.516,0.518,0.520,0.520,0.520,0.520]

EBITDA_MARGIN = [-0.079,-0.250,-0.143,0.175,0.234,0.277,0.186,0.213,0.209,
                 0.261,0.290,0.253,0.260,-0.028,0.285,0.270,0.275,0.282,
                 0.276,0.279,0.281,0.280,0.283,0.277,
                 -0.028,-0.015,0.050,0.055,0.060,0.065,0.068,0.070,0.072,0.072,0.072,0.072]

CONTRIB_MARGIN = [0.371,0.338,0.219,0.377,0.395,0.453,0.418,0.427,0.431,
                  0.458,0.468,0.451,0.456,0.490,0.465,0.460,0.463,0.467,
                  0.462,0.464,0.466,0.468,0.471,0.468,
                  0.490,0.495,0.500,0.502,0.505,0.507,0.510,0.512,0.514,0.514,0.514,0.514]

EBITDA = [v * n for v, n in zip(EBITDA_MARGIN, NET_REVENUE)]

CASH_BALANCE = [59097.96,124340.07,244767.15,231633.68,206271.76,190357.48,
                224853.21,268391.45,290123.67,342156.89,401234.56,438956.23,
                489123.45,525777.08,612890.12,634567.89,678901.23,723456.78,
                756789.01,789012.34,812345.67,845678.9,889012.34,912345.67,
                912345.67,950000,985000,1020000,1060000,1095000,
                1130000,1160000,1195000,1225000,1255000,1285000]

DTC_AOV = [52.87,65.12,56.26,55.58,56.19,57.95,61.09,62.3,61.8,
           63.4,65.1,64.2,65.0,66.1,67.2,66.5,67.8,68.4,
           68.9,69.5,70.1,70.8,71.4,72.0,
           72.0,73.0,74.0,74.5,75.0,75.5,76.0,76.5,77.0,77.0,77.0,77.0]

ROAS = [None,92.14,93.03,51.24,86.54,84.67,78.45,81.23,83.67,
        89.12,91.45,88.76,90.23,88.15,93.45,87.65,89.34,92.12,
        90.67,91.89,93.12,94.45,96.78,95.23,
        93.0,95.0,97.0,98.0,100.0,101.0,102.0,103.0,104.0,104.0,104.0,104.0]

WS_ACCOUNTS = [0,0,37,230,276,265,296,318,334,356,378,390,
               398,406,415,423,431,438,445,452,458,464,470,476,
               480,488,
               495,502,510,518,525,532,540,548,548,548]

UNITS_SOLD = [5557,6141,16119,117154,158559,132072,172578,194357,200205,
              201290,226025,197193,194260,220901,302453,98144,62863,70334,
              91935,75544,88174,86386,76100,110067,87456,74702,
              95137,107112,114630,131551,137729,150634,158791,165991,176897,174901]

# Annual actuals
ANN_2024 = {'gross_sales': 3335807.93, 'net_revenue': 3179765.77,
            'ebitda': 586839.25, 'gross_margin': 0.648, 'net_income': 55055.07}
ANN_2025 = {'gross_sales': 6464850.11, 'net_revenue': 5767748.25,
            'ebitda': 430760.01, 'gross_margin': 0.639, 'net_income': 162704.55}
ANN_2026_BUD = {'gross_sales': 11032457.28, 'net_revenue': 9962290.02,
                'ebitda': -439103.98, 'gross_margin': 0.510, 'net_income': None}

# BvA Feb-26 data
BVA_DATA = {
    'DTC Sales':              (174361.14, 176004.87),
    'Wholesale Sales':        (236298.65, 253331.26),
    'Distributor Sales':      (148156.00, 142372.75),
    'Events Sales':           (25327.57,  19653.40),
    'Gross Sales':            (584143.36, 591362.28),
    'Net Revenue':            (525777.08, 539414.94),
    'Gross Profit':           (259831.00, 243731.29),
    'Total COGS':             (265946.08, 295683.65),
    'Total Fulfillment':      (94137.87,  92838.73),
    'Total Marketing':        (47404.34,  31165.70),
    'Salaries & Wages':       (53063.88,  70273.33),
}

# Build DataFrame
df = pd.DataFrame({
    'label': LABELS,
    'status': STATUS,
    'gross_sales': GROSS_SALES,
    'net_revenue': NET_REVENUE,
    'dtc_sales': DTC_SALES,
    'wholesale_sales': WHOLESALE_SALES,
    'events_sales': EVENTS_SALES,
    'distributor_sales': DISTRIBUTOR_SALES,
    'gross_margin': GROSS_MARGIN,
    'ebitda_margin': EBITDA_MARGIN,
    'contrib_margin': CONTRIB_MARGIN,
    'ebitda': EBITDA,
    'cash_balance': CASH_BALANCE,
    'dtc_aov': DTC_AOV,
    'roas': ROAS,
    'ws_accounts': WS_ACCOUNTS,
    'units_sold': UNITS_SOLD,
})
df['year'] = df['label'].str[-2:].astype(int) + 2000
df['month_idx'] = range(len(df))


# ══════════════════════════════════════════════════════════════════════════════
# CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#9a8c78', size=12),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11), orientation='h',
                y=1.08, x=0),
    xaxis=dict(gridcolor='#1c3450', linecolor='#1c3450', tickfont=dict(size=10)),
)

YAXIS_DEFAULT = dict(gridcolor='#1c3450', linecolor='#1c3450', tickfont=dict(size=10))

# Navy/tan brand palette
C_NAVY   = '#1b3a6b'
C_TAN    = '#c9a84c'
C_TAN2   = '#e8c97a'   # lighter tan
C_NAVY2  = '#2e5f9e'   # lighter navy
C_GREEN  = '#4caf7d'
C_RED    = '#e05c5c'
C_MUTED  = '#5a7a96'   # muted blue-gray

def fmt_k(v):
    if v is None: return 'N/A'
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000: return f"${v/1_000:.0f}K"
    return f"${v:.0f}"

def fmt_pct(v): return f"{v*100:.1f}%" if v is not None else 'N/A'

def delta_html(cur, prior, fmt='dollar', invert=False, label='YoY'):
    if prior is None or prior == 0: return ''
    d = cur - prior
    pct = d / abs(prior)
    pos = d >= 0
    if invert: pos = not pos
    cls = 'pos' if pos else 'neg'
    arrow = '▲' if d >= 0 else '▼'
    if fmt == 'pct':
        s = f"{arrow} {abs(d)*100:.1f}pp {label}"
    else:
        s = f"{arrow} {fmt_k(abs(d))} {label}"
    return f'<div class="kpi-delta {cls}">{s}</div>'

def kpi_card(label, value_str, delta_html_str='', sub='', color='blue'):
    return f"""
    <div class="kpi-card {color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value_str}</div>
      {delta_html_str}
      {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
    </div>"""

def split_act_fcast(dff):
    act = dff[dff['status'] == 'Actuals']
    fcast = dff[dff['status'] == 'Forecast']
    return act, fcast


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — CONTROLS
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🐾 Saint Rocco's")
    st.markdown("**KPI Dashboard**")
    st.markdown("---")

    st.markdown("#### 📅 Date Range")
    year_filter = st.multiselect(
        "Years", options=[2024, 2025, 2026],
        default=[2024, 2025, 2026]
    )
    status_filter = st.multiselect(
        "Data type", options=['Actuals', 'Forecast'],
        default=['Actuals', 'Forecast']
    )

    st.markdown("---")
    st.markdown("#### 🎛️ Scenario Inputs")
    st.caption("Adjust assumptions to pressure test the model")

    dtc_growth = st.slider("DTC Revenue Growth %", 10, 100, 47, step=1,
                           help="YoY growth rate for DTC channel") / 100
    ws_growth = st.slider("Wholesale Revenue Growth %", 20, 150, 99, step=1) / 100
    paid_marketing = st.slider("Paid Marketing Spend ($K)", 50, 500, 138, step=5) * 1000
    gross_margin_tgt = st.slider("Gross Margin Target %", 35, 65, 50, step=1) / 100
    fulfillment_pct = st.slider("Fulfillment % of Net Rev", 10, 35, 18, step=1) / 100
    retention_m1 = st.slider("Month-1 Retention Rate %", 10, 35, 17, step=1) / 100
    dtc_aov_inp = st.slider("DTC AOV ($)", 45, 95, 73, step=1)
    ws_accounts = st.slider("Active Wholesale Accounts", 200, 800, 488, step=10)
    num_events = st.slider("Annual Events", 500, 5000, 2405, step=50)

    st.markdown("---")
    st.caption("Last actualized: **Feb-26**")
    st.caption("Model: StR Financial Model v2026-03-24")


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════

base_dtc_2026 = sum(DTC_SALES[24:])
base_ws_2026  = sum(WHOLESALE_SALES[24:])
base_nr_2025  = ANN_2025['net_revenue']

scen_dtc_2026     = base_dtc_2026 * (1 + dtc_growth) / (1 + 0.47)
scen_ws_2026      = base_ws_2026 * (1 + ws_growth) / (1 + 0.99)
scen_gross_sales  = scen_dtc_2026 + scen_ws_2026 + sum(EVENTS_SALES[24:]) + sum(DISTRIBUTOR_SALES[24:])
scen_net_rev      = scen_gross_sales * 0.933
scen_gross_profit = scen_net_rev * gross_margin_tgt
scen_cogs         = scen_net_rev - scen_gross_profit
scen_fulfillment  = scen_net_rev * fulfillment_pct
scen_marketing    = paid_marketing + scen_net_rev * 0.04
scen_people       = 4_773_900
scen_admin        = scen_net_rev * 0.06
scen_total_opex   = scen_fulfillment + scen_marketing + scen_people + scen_admin
scen_ebitda       = scen_gross_profit - scen_total_opex
scen_ebitda_margin = scen_ebitda / scen_net_rev if scen_net_rev else 0

base_ebitda_2026  = ANN_2026_BUD['ebitda']
delta_ebitda      = scen_ebitda - base_ebitda_2026

# New customers estimate
avg_ws_sales_per_acct = 450
scen_ws_revenue_est = ws_accounts * avg_ws_sales_per_acct * 12
events_customers = num_events * 1.2
paid_customers = paid_marketing / 43.3 if paid_marketing > 0 else 0
total_new_custs = events_customers + paid_customers


# ══════════════════════════════════════════════════════════════════════════════
# FILTER DATA
# ══════════════════════════════════════════════════════════════════════════════

dff = df[df['year'].isin(year_filter) & df['status'].isin(status_filter)].copy()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:4px;">
  <span style="font-size:28px">🐾</span>
  <div>
    <div style="font-size:22px; font-weight:600; color:#f1f5f9; line-height:1.2;">
      Saint Rocco's  ·  Executive KPI Dashboard
    </div>
    <div style="font-size:13px; color:#64748b;">
      Last actualized: Feb-26  ·  Source: StR Financial Model v2026-03-24
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Performance",
    "📈  Revenue Trends",
    "🎛️  Scenario Model",
    "📋  Budget vs Actual",
])


# ╔══════════════════════════════════════════════════════════════════════════════
# TAB 1: PERFORMANCE SCORECARD
# ╔══════════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown('<div class="section-header">FY2025 Actuals vs FY2024</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    # FY26 YTD = Jan-26 + Feb-26 (indices 24, 25)
    # FY25 YTD = Jan-25 + Feb-25 (indices 12, 13)
    ytd26_gs  = sum(GROSS_SALES[24:26])
    ytd25_gs  = sum(GROSS_SALES[12:14])
    ytd26_nr  = sum(NET_REVENUE[24:26])
    ytd25_nr  = sum(NET_REVENUE[12:14])
    ytd26_eb  = sum(EBITDA[24:26])
    ytd25_eb  = sum(EBITDA[12:14])
    ytd26_gm  = sum(GROSS_MARGIN[24:26]) / 2
    ytd25_gm  = sum(GROSS_MARGIN[12:14]) / 2

    st.markdown('<div class="section-header">FY2026 YTD vs FY2025 YTD  ·  Jan – Feb</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        d = delta_html(ytd26_gs, ytd25_gs)
        st.markdown(kpi_card("FY26 YTD Gross Sales", fmt_k(ytd26_gs), d,
                             sub=f"FY25 YTD: {fmt_k(ytd25_gs)}", color='navy'), unsafe_allow_html=True)
    with c2:
        d = delta_html(ytd26_nr, ytd25_nr)
        st.markdown(kpi_card("FY26 YTD Net Revenue", fmt_k(ytd26_nr), d,
                             sub=f"FY25 YTD: {fmt_k(ytd25_nr)}", color='tan'), unsafe_allow_html=True)
    with c3:
        d = delta_html(ytd26_gm, ytd25_gm, fmt='pct')
        st.markdown(kpi_card("FY26 YTD Gross Margin", fmt_pct(ytd26_gm), d,
                             sub=f"FY25 YTD: {fmt_pct(ytd25_gm)}", color='green'), unsafe_allow_html=True)
    with c4:
        d = delta_html(ytd26_eb, ytd25_eb)
        st.markdown(kpi_card("FY26 YTD EBITDA", fmt_k(ytd26_eb), d,
                             sub=f"FY25 YTD: {fmt_k(ytd25_eb)}", color='tan'), unsafe_allow_html=True)

    st.markdown("")
    c5, c6, c7, c8 = st.columns(4)

    # Latest actuals (Feb-26 = index 25)
    feb26 = df.iloc[25]
    feb25 = df.iloc[13]

    with c5:
        ytd26_dtc = sum(DTC_SALES[24:26])
        ytd25_dtc = sum(DTC_SALES[12:14])
        d = delta_html(ytd26_dtc, ytd25_dtc, label='vs FY25 YTD')
        st.markdown(kpi_card("FY26 YTD DTC Sales", fmt_k(ytd26_dtc), d,
                             sub=f"FY25 YTD: {fmt_k(ytd25_dtc)}", color='navy'), unsafe_allow_html=True)
    with c6:
        d = delta_html(feb26['ws_accounts'], feb25['ws_accounts'], label='vs Feb-25')
        st.markdown(kpi_card("Wholesale Accts (Feb-26)", f"{int(feb26['ws_accounts'])}", d,
                             sub="Active accounts that ordered", color='tan'), unsafe_allow_html=True)
    with c7:
        roas_val = feb26['roas']
        st.markdown(kpi_card("DTC ROAS (Feb-26)", f"{roas_val:.1f}x" if roas_val else 'N/A',
                             sub="Gross Sales / Paid Spend", color='tan'), unsafe_allow_html=True)
    with c8:
        d = delta_html(feb26['cash_balance'], feb25['cash_balance'], label='vs Feb-25')
        st.markdown(kpi_card("Cash Balance (Feb-26)", fmt_k(feb26['cash_balance']), d, color='green'), unsafe_allow_html=True)

    # ── Annual comparison bar chart ───────────────────────────────────────────
    st.markdown('<div class="section-header">Annual Summary  ·  FY2024 · FY2025 · FY2026 Budget</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        fig = go.Figure()
        years = ['FY2024', 'FY2025', 'FY2026 Budget']
        gs_vals = [ANN_2024['gross_sales'], ANN_2025['gross_sales'], ANN_2026_BUD['gross_sales']]
        nr_vals = [ANN_2024['net_revenue'], ANN_2025['net_revenue'], ANN_2026_BUD['net_revenue']]

        fig.add_trace(go.Bar(name='Gross Sales', x=years, y=gs_vals,
                             marker_color=C_NAVY, marker_line_width=0))
        fig.add_trace(go.Bar(name='Net Revenue', x=years, y=nr_vals,
                             marker_color=C_TAN, marker_line_width=0))
        fig.update_layout(**PLOTLY_LAYOUT, title='Revenue ($)', barmode='group',
                          yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        fig2 = go.Figure()
        eb_vals = [ANN_2024['ebitda'], ANN_2025['ebitda'], ANN_2026_BUD['ebitda']]
        ni_vals = [ANN_2024['net_income'], ANN_2025['net_income'], 0]
        fig2.add_trace(go.Bar(name='EBITDA', x=years, y=eb_vals,
                              marker_color=[C_TAN, C_TAN, C_MUTED],
                              marker_line_width=0))
        fig2.add_trace(go.Bar(name='Net Income', x=years, y=ni_vals,
                              marker_color=[C_GREEN, C_GREEN, C_MUTED],
                              marker_line_width=0))
        fig2.update_layout(**PLOTLY_LAYOUT, title='Profitability ($)', barmode='group',
                           yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Margin comparison ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Margin Trends — FY2024 vs FY2025</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    metrics_comp = [
        ("Gross Margin", ANN_2024['gross_margin'], ANN_2025['gross_margin'], 'green'),
        ("EBITDA Margin", ANN_2024['ebitda']/ANN_2024['net_revenue'],
         ANN_2025['ebitda']/ANN_2025['net_revenue'], 'tan'),
        ("Net Income Margin", ANN_2024['net_income']/ANN_2024['net_revenue'],
         ANN_2025['net_income']/ANN_2025['net_revenue'], 'navy'),
    ]
    for col, (lbl, v24, v25, clr) in zip([col_a, col_b, col_c], metrics_comp):
        with col:
            d = delta_html(v25, v24, fmt='pct', label='vs FY2024')
            st.markdown(kpi_card(lbl, fmt_pct(v25), d,
                                 sub=f"FY2024: {fmt_pct(v24)}", color=clr), unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════════
# TAB 2: REVENUE TRENDS
# ╔══════════════════════════════════════════════════════════════════════════════

with tab2:

    if dff.empty:
        st.warning("No data for selected filters.")
    else:
        act, fcast = split_act_fcast(dff)

        # ── Revenue by channel stacked bar ────────────────────────────────────
        st.markdown('<div class="section-header">Revenue by Channel</div>', unsafe_allow_html=True)
        fig = go.Figure()

        channels = [
            ('dtc_sales',          'DTC',          C_NAVY),
            ('wholesale_sales',     'Wholesale',    C_TAN),
            ('distributor_sales',   'Distributor',  C_NAVY2),
            ('events_sales',        'Events',       C_TAN2),
        ]
        for col, name, color in channels:
            if not act.empty:
                fig.add_trace(go.Bar(name=name, x=act['label'], y=act[col],
                                     marker_color=color, marker_line_width=0,
                                     legendgroup=name))
            if not fcast.empty:
                fig.add_trace(go.Bar(name=f'{name} (Forecast)', x=fcast['label'],
                                     y=fcast[col],
                                     marker_color=color, opacity=0.45,
                                     marker_line_width=0, marker_pattern_shape='/',
                                     legendgroup=name, showlegend=False))

        fig.update_layout(**PLOTLY_LAYOUT, barmode='stack', height=340,
                          title='Monthly Gross Sales by Channel ($)',
                          yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
        st.plotly_chart(fig, use_container_width=True)

        # ── Margin trends ──────────────────────────────────────────────────────
        st.markdown('<div class="section-header">Margin Trends</div>', unsafe_allow_html=True)
        fig2 = go.Figure()

        margin_series = [
            ('gross_margin',   'Gross Margin',         C_TAN,   'solid'),
            ('contrib_margin', 'Contribution Margin',  C_NAVY2, 'solid'),
            ('ebitda_margin',  'EBITDA Margin',        C_GREEN, 'solid'),
        ]
        for col, name, color, dash in margin_series:
            if not act.empty:
                fig2.add_trace(go.Scatter(
                    x=act['label'], y=act[col], name=name,
                    line=dict(color=color, width=2, dash=dash),
                    mode='lines'))
            if not fcast.empty:
                fig2.add_trace(go.Scatter(
                    x=fcast['label'], y=fcast[col], name=f'{name} (F)',
                    line=dict(color=color, width=2, dash='dot'),
                    mode='lines', showlegend=False))

        fig2.add_hline(y=0, line_dash='dash', line_color='#ef4444', opacity=0.5)
        fig2.update_layout(**PLOTLY_LAYOUT, height=300,
                           yaxis=dict(**YAXIS_DEFAULT, tickformat='.0%'))
        st.plotly_chart(fig2, use_container_width=True)

        # ── EBITDA and Cash ───────────────────────────────────────────────────
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="section-header">Monthly EBITDA</div>', unsafe_allow_html=True)
            fig3 = go.Figure()
            colors_ebitda = [C_GREEN if v >= 0 else C_RED for v in dff['ebitda']]
            fig3.add_trace(go.Bar(x=dff['label'], y=dff['ebitda'],
                                  marker_color=colors_ebitda, marker_line_width=0,
                                  name='EBITDA'))
            fig3.add_hline(y=0, line_dash='dash', line_color='#64748b', opacity=0.6)
            fig3.update_layout(**PLOTLY_LAYOUT, height=280,
                               yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
            st.plotly_chart(fig3, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-header">Cash Balance</div>', unsafe_allow_html=True)
            fig4 = go.Figure()
            if not act.empty:
                fig4.add_trace(go.Scatter(x=act['label'], y=act['cash_balance'],
                                          fill='tozeroy', fillcolor='rgba(201,168,76,0.12)',
                                          line=dict(color=C_TAN, width=2),
                                          name='Cash Balance'))
            if not fcast.empty:
                fig4.add_trace(go.Scatter(x=fcast['label'], y=fcast['cash_balance'],
                                          line=dict(color=C_TAN, width=2, dash='dot'),
                                          name='Forecast', showlegend=False))
            fig4.update_layout(**PLOTLY_LAYOUT, height=280,
                               yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
            st.plotly_chart(fig4, use_container_width=True)

        # ── Channel mix & operating metrics ──────────────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-header">FY2025 Revenue Mix</div>', unsafe_allow_html=True)
            yr25 = df[df['year'] == 2025]
            mix_vals = [yr25['dtc_sales'].sum(), yr25['wholesale_sales'].sum(),
                        yr25['distributor_sales'].sum(), yr25['events_sales'].sum()]
            mix_lbls = ['DTC', 'Wholesale', 'Distributor', 'Events']
            fig5 = go.Figure(go.Pie(
                labels=mix_lbls, values=mix_vals,
                hole=0.55, marker_colors=[C_NAVY, C_TAN, C_NAVY2, C_TAN2],
                textfont=dict(color='#f0e6d3', size=12),
            ))
            pie_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != 'legend'}
            fig5.update_layout(**pie_layout, height=280,
                               yaxis=dict(**YAXIS_DEFAULT),
                               showlegend=True,
                               legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11),
                                           orientation='h', y=-0.05))
            st.plotly_chart(fig5, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">DTC AOV & Wholesale Accounts</div>', unsafe_allow_html=True)
            fig6 = make_subplots(specs=[[{"secondary_y": True}]])
            fig6.add_trace(go.Scatter(x=dff['label'], y=dff['dtc_aov'],
                                      name='DTC AOV ($)',
                                      line=dict(color=C_TAN, width=2)), secondary_y=False)
            fig6.add_trace(go.Scatter(x=dff['label'], y=dff['ws_accounts'],
                                      name='Wholesale Accounts',
                                      line=dict(color=C_NAVY2, width=2, dash='dot')), secondary_y=True)
            fig6.update_layout(**PLOTLY_LAYOUT, height=280)
            fig6.update_yaxes(tickprefix='$', gridcolor='#1e2535', secondary_y=False)
            fig6.update_yaxes(gridcolor='#1e2535', secondary_y=True)
            st.plotly_chart(fig6, use_container_width=True)


# ╔══════════════════════════════════════════════════════════════════════════════
# TAB 3: SCENARIO MODEL
# ╔══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown(f"""
    <div class="scenario-banner">
      <strong>Scenario Mode</strong> — Use the sliders in the left panel to pressure test assumptions.
      Results below update in real time based on your inputs.
    </div>""", unsafe_allow_html=True)

    # Top KPIs from scenario
    st.markdown('<div class="section-header">FY2026 Scenario Output</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        d = delta_html(scen_gross_sales, ANN_2026_BUD['gross_sales'], label='vs Budget')
        st.markdown(kpi_card("Scenario Gross Sales", fmt_k(scen_gross_sales), d, color='blue'), unsafe_allow_html=True)
    with c2:
        d = delta_html(scen_net_rev, ANN_2026_BUD['net_revenue'], label='vs Budget')
        st.markdown(kpi_card("Scenario Net Revenue", fmt_k(scen_net_rev), d, color='teal'), unsafe_allow_html=True)
    with c3:
        em_base = ANN_2026_BUD['ebitda'] / ANN_2026_BUD['net_revenue']
        d = delta_html(scen_ebitda_margin, em_base, fmt='pct', label='vs Budget')
        st.markdown(kpi_card("Scenario EBITDA Margin", fmt_pct(scen_ebitda_margin), d, color='amber'), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Scenario EBITDA", fmt_k(scen_ebitda),
                             delta_html(scen_ebitda, base_ebitda_2026, label='vs Budget'),
                             color='green' if scen_ebitda >= 0 else 'red'), unsafe_allow_html=True)

    st.markdown("")
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(kpi_card("Est. New Customers", f"{int(total_new_custs):,}",
                             sub=f"Paid: {int(paid_customers):,}  |  Events: {int(events_customers):,}", color='purple'), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("DTC AOV (Input)", f"${dtc_aov_inp}", color='indigo'), unsafe_allow_html=True)
    with c7:
        st.markdown(kpi_card("Month-1 Retention", fmt_pct(retention_m1), color='rose'), unsafe_allow_html=True)
    with c8:
        st.markdown(kpi_card("Marketing as % Rev", fmt_pct(scen_marketing/scen_net_rev if scen_net_rev else 0), color='amber'), unsafe_allow_html=True)

    # ── Waterfall P&L ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Scenario P&L Waterfall — FY2026</div>', unsafe_allow_html=True)

    wf_labels = ['Net Revenue', 'COGS', 'Gross Profit', 'Fulfillment',
                 'Marketing', 'People', 'Admin & Other', 'EBITDA']
    wf_values = [scen_net_rev, -scen_cogs, scen_gross_profit, -scen_fulfillment,
                 -scen_marketing, -scen_people, -scen_admin, scen_ebitda]
    wf_colors = ['#3b82f6','#ef4444','#14b8a6','#f59e0b','#f59e0b','#f59e0b','#f59e0b',
                 '#22c55e' if scen_ebitda >= 0 else '#ef4444']

    fig_wf = go.Figure(go.Waterfall(
        name='FY2026 Scenario', orientation='v',
        measure=['absolute','relative','total','relative','relative','relative','relative','total'],
        x=wf_labels,
        y=wf_values,
        connector={'line': {'color': '#2d3a52'}},
        decreasing={'marker': {'color': '#ef4444'}},
        increasing={'marker': {'color': '#22c55e'}},
        totals={'marker': {'color': '#3b82f6'}},
        text=[fmt_k(v) for v in wf_values],
        textposition='outside',
        textfont=dict(color='#c8d0e0', size=11),
    ))
    fig_wf.update_layout(**PLOTLY_LAYOUT, height=380,
                         yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
    st.plotly_chart(fig_wf, use_container_width=True)

    # ── Scenario sensitivity table ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Sensitivity Analysis — EBITDA vs Growth Assumptions</div>', unsafe_allow_html=True)
    st.caption("EBITDA at different combinations of DTC growth and gross margin (holding all other inputs constant)")

    dtc_range = [0.20, 0.30, 0.40, 0.47, 0.55, 0.65, 0.80]
    gm_range  = [0.38, 0.42, 0.46, 0.50, 0.54, 0.58]

    rows = []
    for gm in gm_range:
        row = {}
        for dtc_g in dtc_range:
            _gs  = base_dtc_2026 * (1 + dtc_g) / (1 + 0.47) + scen_ws_2026 + sum(EVENTS_SALES[24:]) + sum(DISTRIBUTOR_SALES[24:])
            _nr  = _gs * 0.933
            _gp  = _nr * gm
            _eb  = _gp - (_nr * fulfillment_pct + paid_marketing + _nr * 0.04 + scen_people + _nr * 0.06)
            row[f"{int(dtc_g*100)}%"] = _eb
        rows.append(row)

    sens_df = pd.DataFrame(rows, index=[f"GM {int(g*100)}%" for g in gm_range])

    def highlight_ebitda(val):
        if isinstance(val, float):
            if val > 500_000: return 'background-color:#14532d; color:#86efac'
            if val > 0: return 'background-color:#166534; color:#bbf7d0'
            if val > -500_000: return 'background-color:#7f1d1d; color:#fca5a5'
            return 'background-color:#450a0a; color:#fca5a5'
        return ''

    styled = sens_df.applymap(lambda v: fmt_k(v) if isinstance(v, float) else v)
    st.dataframe(
        styled.style.applymap(highlight_ebitda, subset=pd.IndexSlice[:, :]),
        use_container_width=True
    )
    st.caption("Column = DTC YoY growth rate  ·  Row = Gross Margin %  ·  Current scenario highlighted at intersection")


# ╔══════════════════════════════════════════════════════════════════════════════
# TAB 4: BUDGET vs ACTUAL
# ╔══════════════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown('<div class="section-header">Budget vs Actual  ·  Month Ending February 2026</div>', unsafe_allow_html=True)

    def bva_row_html(label, actual, budget, section=False):
        if section:
            return f'<tr class="section-row"><td colspan="5">{label}</td></tr>'
        var = actual - budget if actual is not None and budget is not None else None
        pct = var / abs(budget) if var is not None and budget else None
        var_cls = 'pos-var' if (var or 0) >= 0 else 'neg-var'
        arr = '▲' if (var or 0) >= 0 else '▼'
        return f"""<tr>
          <td>{label}</td>
          <td>{fmt_k(actual)}</td>
          <td>{fmt_k(budget)}</td>
          <td class="{var_cls}">{fmt_k(var)}</td>
          <td class="{var_cls}">{arr} {fmt_pct(abs(pct)) if pct is not None else '—'}</td>
        </tr>"""

    html_rows = ""
    sections = {
        'Revenue': ['DTC Sales','Wholesale Sales','Distributor Sales','Events Sales','Gross Sales','Net Revenue'],
        'Profitability': ['Gross Profit','Total COGS','Total Fulfillment','Total Marketing','Salaries & Wages'],
    }
    for section, items in sections.items():
        html_rows += bva_row_html(section, None, None, section=True)
        for item in items:
            if item in BVA_DATA:
                actual, budget = BVA_DATA[item]
                html_rows += bva_row_html(item, actual, budget)

    st.markdown(f"""
    <table class="bva-table">
      <thead>
        <tr>
          <th>Line Item</th><th>Actual</th><th>Budget</th>
          <th>$ Variance</th><th>% Variance</th>
        </tr>
      </thead>
      <tbody>{html_rows}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BvA bar chart ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Actual vs Budget — Revenue Lines</div>', unsafe_allow_html=True)

    rev_lines = ['DTC Sales','Wholesale Sales','Distributor Sales','Events Sales','Net Revenue']
    actuals_bva  = [BVA_DATA[k][0] for k in rev_lines]
    budgets_bva  = [BVA_DATA[k][1] for k in rev_lines]

    fig_bva = go.Figure()
    fig_bva.add_trace(go.Bar(name='Actual', x=rev_lines, y=actuals_bva,
                              marker_color=C_NAVY, marker_line_width=0))
    fig_bva.add_trace(go.Bar(name='Budget', x=rev_lines, y=budgets_bva,
                              marker_color=C_MUTED, marker_line_width=0, opacity=0.7))
    fig_bva.update_layout(**PLOTLY_LAYOUT, barmode='group', height=320,
                           yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
    st.plotly_chart(fig_bva, use_container_width=True)

    # ── Variance chart ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Variance from Budget ($)</div>', unsafe_allow_html=True)

    all_items = list(BVA_DATA.keys())
    variances = [BVA_DATA[k][0] - BVA_DATA[k][1] for k in all_items]
    var_colors = [C_GREEN if v >= 0 else C_RED for v in variances]

    fig_var = go.Figure(go.Bar(
        x=all_items, y=variances,
        marker_color=var_colors, marker_line_width=0,
        text=[fmt_k(v) for v in variances], textposition='outside',
        textfont=dict(color='#c8d0e0', size=10),
    ))
    fig_var.add_hline(y=0, line_dash='dash', line_color='#64748b')
    fig_var.update_layout(**PLOTLY_LAYOUT, height=300,
                           yaxis=dict(**YAXIS_DEFAULT, tickformat='$,.0f'))
    st.plotly_chart(fig_var, use_container_width=True)
