#!/usr/bin/env python3

"""
forecast.py – Core financial forecast engine (Python ≥ 3.12.3)
==============================================================
Part of the *Pack 3 – Prévisions & Accompagnement* demo project.

This module provides a lightweight, fully‑typed simulator that forecasts a
SaaS B2B P&L and cash‑flow over *n* months for a single scenario (Base,
Pessimistic, Ambitious, etc.).  All amounts are expressed in **EUR**.

Public API
~~~~~~~~~~
* ``Scenario`` – a frozen ``@dataclass`` bundling the main drivers.
* ``simulate``  – returns a ``pandas.DataFrame`` with monthly metrics.


Dependencies
~~~~~~~~~~~~
* ``pandas >= 2.2``
* ``numpy  >= 2.0``

Design notes
~~~~~~~~~~~~
* No external I/O – integration with Excel, Streamlit or API layers happens
  elsewhere.
* Pure functions → easy to unit‑test and reuse.
"""
from __future__ import annotations  # Postponed evaluation of annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

import numpy as np
import pandas as pd

__all__ = [
    "Scenario",
    "simulate",
]


@dataclass(slots=True, frozen=True)
class Scenario:
    """Business drivers for one forecast scenario.

    Percentages are supplied as decimals (e.g. 5% → ``0.05``).
    Monetary values are **monthly** amounts in EUR.
    """

    name: str
    growth: float    # Monthly *net* growth of MRR before churn
    churn: float     # Monthly churn rate
    cogs_pct: float  # COGS as a percentage of revenue
    opex_rnd: float  # Fixed Opex – R&D
    opex_sm: float   # Fixed Opex – Sales & Marketing
    opex_ga: float   # Fixed Opex – G&A

    # Python 3.12 adds typing.Self, but here a dict is more convenient.
    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON‑serialisable representation."""
        return {
            "name": self.name,
            "growth": self.growth,
            "churn": self.churn,
            "cogs_pct": self.cogs_pct,
            "opex_rnd": self.opex_rnd,
            "opex_sm": self.opex_sm,
            "opex_ga": self.opex_ga,
        }


# ---------------------------------------------------------------------------
# Core simulation engine
# ---------------------------------------------------------------------------

def simulate(
    start_date: datetime,
    months: int,
    mrr0: float,
    initial_cash: float,
    scenario: Scenario,
) -> pd.DataFrame:
    """Simulate monthly SaaS metrics over *months* periods.

    Parameters
    ----------
    start_date : datetime
        First month of the forecast (typically the next month).
    months : int
        Number of periods to project (e.g. ``36`` for 3 years).
    mrr0 : float
        Monthly recurring revenue at *start_date*.
    initial_cash : float
        Cash on hand at *start_date* **before** that month’s operations.
    scenario : Scenario
        Business drivers for this projection.

    Returns
    -------
    pandas.DataFrame
        One row per month with columns:
        ``month``, ``date``, ``mrr``, ``revenue``, ``cogs``,
        ``gross_profit``, ``opex_rnd``, ``opex_sm``, ``opex_ga``,
        ``ebitda``, ``operating_cf``, ``cash_balance``.
    """
    if months <= 0:
        raise ValueError("`months` must be strictly positive")

    periods = pd.date_range(start=start_date, periods=months, freq="MS")

    # --- Vectorised calculations ------------------------------------------------
    mrr = np.empty(months, dtype=float)
    mrr[0] = mrr0
    for t in range(1, months):
        mrr[t] = mrr[t - 1] * (1 + scenario.growth - scenario.churn)

    revenue = mrr.copy()  # For pure‑play SaaS, monthly revenue == MRR
    cogs = revenue * scenario.cogs_pct
    gross_profit = revenue - cogs

    # Fixed Opex arrays
    opex_rnd = np.full(months, scenario.opex_rnd)
    opex_sm  = np.full(months, scenario.opex_sm)
    opex_ga  = np.full(months, scenario.opex_ga)

    ebitda = gross_profit - (opex_rnd + opex_sm + opex_ga)
    operating_cf = ebitda  # Simplification: no net working‑capital change

    cash_balance = np.empty(months, dtype=float)
    cash_balance[0] = initial_cash + operating_cf[0]
    for t in range(1, months):
        cash_balance[t] = cash_balance[t - 1] + operating_cf[t]

    df = pd.DataFrame(
        {
            "month": np.arange(1, months + 1),
            "date": periods,
            "mrr": mrr,
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "opex_rnd": opex_rnd,
            "opex_sm": opex_sm,
            "opex_ga": opex_ga,
            "ebitda": ebitda,
            "operating_cf": operating_cf,
            "cash_balance": cash_balance,
        }
    )

    # Attach metadata for downstream consumers
    df.attrs["scenario"] = scenario.as_dict()
    df.attrs["generated_on"] = pd.Timestamp.utcnow()

    return df


# ---------------------------------------------------------------------------
# Manual test (run: python forecast.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    base = Scenario(
        "Base",
        growth=0.05,
        churn=0.03,
        cogs_pct=0.15,
        opex_rnd=15_000,
        opex_sm=12_000,
        opex_ga=8_000,
    )
    result = simulate(
        datetime(2025, 9, 1),
        months=36,
        mrr0=50_000,
        initial_cash=100_000,
        scenario=base,
    )
    print(result.head())
