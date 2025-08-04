"""app/main.py – Streamlit UI for Pack‑3 demo
================================================
Run locally with:
    streamlit run app/main.py
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Ensure repo root is on sys.path so `import model.forecast` works regardless
# of where `streamlit run` is executed from (IDE, subfolder, etc.).
# ---------------------------------------------------------------------------
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import io
from datetime import datetime
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Local business logic
from model.forecast import Scenario, simulate  # noqa: E402

st.set_page_config(
    page_title="Pack 3 Forecast Demo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar – scenario selection & inputs
# ---------------------------------------------------------------------------
st.sidebar.title("Paramètres / Settings")

DEFAULT_SCENARIOS: Dict[str, Scenario] = {
    "Base": Scenario(
        "Base", growth=0.05, churn=0.03, cogs_pct=0.15,
        opex_rnd=15_000, opex_sm=12_000, opex_ga=8_000,
    ),
    "Pessimiste": Scenario(
        "Pessimiste", growth=0.03, churn=0.05, cogs_pct=0.17,
        opex_rnd=16_000, opex_sm=13_000, opex_ga=9_000,
    ),
    "Ambitieux": Scenario(
        "Ambitieux", growth=0.08, churn=0.02, cogs_pct=0.13,
        opex_rnd=14_000, opex_sm=11_000, opex_ga=7_000,
    ),
}

selected_label = st.sidebar.selectbox(
    "Choisissez un scénario ou personnalisez ⬇", list(DEFAULT_SCENARIOS.keys())
)
base_scenario = DEFAULT_SCENARIOS[selected_label]

st.sidebar.divider()
st.sidebar.markdown("### Ajustez les hypothèses (facultatif)")

growth = st.sidebar.slider("Croissance mensuelle (%)", 0.0, 0.2, base_scenario.growth, 0.005)
churn = st.sidebar.slider("Churn mensuel (%)", 0.0, 0.2, base_scenario.churn, 0.005)
cogs_pct = st.sidebar.slider("COGS / Revenue (%)", 0.0, 0.5, base_scenario.cogs_pct, 0.01)

st.sidebar.markdown("#### Opex fixes (€ / mois)")
opex_rnd = st.sidebar.number_input("R&D", min_value=0, step=1000, value=int(base_scenario.opex_rnd))
opex_sm = st.sidebar.number_input("Sales & Marketing", min_value=0, step=1000, value=int(base_scenario.opex_sm))
opex_ga = st.sidebar.number_input("G&A", min_value=0, step=1000, value=int(base_scenario.opex_ga))

st.sidebar.divider()
months = st.sidebar.slider("Période (mois)", 12, 60, 36, 12)
start_dt = st.sidebar.date_input("Date de départ", datetime(2025, 9, 1)).replace(day=1)
initial_mrr = st.sidebar.number_input("MRR initial (€)", min_value=0, step=1000, value=50_000)
initial_cash = st.sidebar.number_input("Trésorerie initiale (€)", min_value=0, step=1000, value=100_000)

scenario = Scenario(
    base_scenario.name,
    growth=growth,
    churn=churn,
    cogs_pct=cogs_pct,
    opex_rnd=opex_rnd,
    opex_sm=opex_sm,
    opex_ga=opex_ga,
)

# ---------------------------------------------------------------------------
# Run simulation (cached)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def run_simulation(start: datetime, months: int, mrr0: float, cash0: float, s: Scenario) -> pd.DataFrame:  # noqa: E501
    """Wrapper around simulate() so that results are memoized by Streamlit."""
    return simulate(start, months, mrr0, cash0, s)

df = run_simulation(start_dt, months, initial_mrr, initial_cash, scenario)

# ---------------------------------------------------------------------------
# Main layout – KPIs & charts
# ---------------------------------------------------------------------------
st.title("Prévisions financières – Demo Pack 3")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    arr_m12 = df.loc[11, "mrr"] * 12 if len(df) >= 12 else np.nan
    st.metric("ARR mois 12 (€)", f"{arr_m12:,.0f}€")
with col_kpi2:
    runway_months = next((i for i, x in enumerate(df["cash_balance"], 1) if x < 0), "≥" + str(months))
    st.metric("Runway (mois)", runway_months)
with col_kpi3:
    st.metric("EBITDA mois 1 (€)", f"{df.loc[0, 'ebitda']:,.0f}€")

fig_cash = px.line(df, x="date", y="cash_balance", title="Trésorerie prévisionnelle")
fig_rev  = px.line(df, x="date", y="revenue", title="Revenu mensuel (MRR)")
fig_ebit = px.line(df, x="date", y="ebitda", title="EBITDA mensuel")

st.plotly_chart(fig_cash, use_container_width=True)
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.plotly_chart(fig_rev, use_container_width=True)
with col_chart2:
    st.plotly_chart(fig_ebit, use_container_width=True)

with st.expander("Afficher le tableau détaillé"):
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------------------------
# Export – CSV & Excel
# ---------------------------------------------------------------------------
# CSV in memory
csv_buf = io.StringIO()
df.to_csv(csv_buf, index=False)
csv_buf.seek(0)  # Important – reposition cursor at start

# Excel in memory
xlsx_buf = io.BytesIO()
with pd.ExcelWriter(xlsx_buf, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Forecast")

    # Access underlying workbook to set document properties
    workbook = writer.book  # ← xlsxwriter.Workbook instance
    workbook.set_properties({
        "title":   "Pack 3 Forecast Export",
        "subject": scenario.name,
    })
# After exiting the with‑block the workbook is saved, so rewind buffer
xlsx_buf.seek(0)

# Download buttons
st.download_button(
    label="📥 Télécharger CSV",
    data=csv_buf.getvalue(),
    file_name="forecast_pack3.csv",
    mime="text/csv",
)

st.download_button(
    label="📥 Télécharger Excel",
    data=xlsx_buf.getvalue(),
    file_name="forecast_pack3.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
