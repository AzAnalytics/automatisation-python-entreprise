"""tests/test_forecast.py – unit tests for model/forecast.py
================================================================
Run with :
    pytest -q               # from repo root (venv activated)
"""
from datetime import datetime

# ---------------------------------------------------------------------------
# Ensure the project root (one level above this tests/ folder) is on sys.path
# so that `import model` resolves whether pytest is launched from the repo root
# or directly inside the tests/ directory (IDE run‑config).
# ---------------------------------------------------------------------------
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))



import numpy as np
import pandas as pd
import pytest

# The engine now lives in model/forecast.py
from model.forecast import Scenario, simulate  # type: ignore


@pytest.fixture(scope="module")
def base_scenario() -> Scenario:
    """A reusable *Base* scenario for most checks."""
    return Scenario(
        "Base", growth=0.05, churn=0.03, cogs_pct=0.15,
        opex_rnd=15_000, opex_sm=12_000, opex_ga=8_000,
    )


def test_length_and_columns(base_scenario: Scenario) -> None:
    """simulate() returns a DataFrame of the requested length and columns."""
    df = simulate(datetime(2025, 9, 1), 36, 50_000, 100_000, base_scenario)
    assert len(df) == 36
    expected_cols = {
        "month", "date", "mrr", "revenue", "cogs", "gross_profit",
        "opex_rnd", "opex_sm", "opex_ga", "ebitda", "operating_cf",
        "cash_balance",
    }
    assert set(df.columns) == expected_cols


def test_negative_months_raises(base_scenario: Scenario) -> None:
    """Passing months <= 0 should raise ValueError."""
    with pytest.raises(ValueError):
        simulate(datetime(2025, 9, 1), 0, 50_000, 100_000, base_scenario)


def test_cash_flow_consistency(base_scenario: Scenario) -> None:
    """Δcash == operating_cf (simplified assumption in the model)."""
    df = simulate(datetime(2025, 9, 1), 12, 50_000, 100_000, base_scenario)
    # cash_balance[t] - cash_balance[t-1] should equal operating_cf[t]
    delta_cash = df["cash_balance"].diff().fillna(df["cash_balance"].iloc[0] - 100_000)
    assert np.allclose(delta_cash.values, df["operating_cf"].values)


def test_attrs_metadata(base_scenario: Scenario) -> None:
    """Scenario metadata is attached to DataFrame attrs."""
    df = simulate(datetime(2025, 9, 1), 6, 50_000, 100_000, base_scenario)
    meta = df.attrs.get("scenario", {})
    assert meta.get("name") == "Base"
    # Must contain at least the keys below
    for key in ("growth", "churn", "cogs_pct"):
        assert key in meta
