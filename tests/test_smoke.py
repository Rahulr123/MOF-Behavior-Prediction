"""Smoke tests — verify the package imports and basic plumbing works.

These tests don't touch the network. They confirm:
- the package and its subpackages import cleanly
- metrics produce sensible values on toy data
- the loader and aggregator functions are callable
- the per-MOF aggregation produces the expected shape on synthetic data
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import mofwater
from mofwater.data import load_odac25, min_h2o_binding_per_mof
from mofwater.eval import mae, r2, rmse


def test_package_has_version() -> None:
    assert isinstance(mofwater.__version__, str)
    assert mofwater.__version__


def test_metrics_on_perfect_predictions() -> None:
    y = np.array([1.0, 2.0, 3.0, 4.0])
    assert rmse(y, y) == 0.0
    assert mae(y, y) == 0.0
    assert r2(y, y) == 1.0


def test_metrics_on_offset_predictions() -> None:
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = y_true + 1.0
    assert rmse(y_true, y_pred) == 1.0
    assert mae(y_true, y_pred) == 1.0
    assert r2(y_true, y_pred) < 1.0


def test_loaders_are_callable() -> None:
    """The loader and aggregator are importable and callable. Network
    behavior is tested by actually running scripts/build_dataset.py — we
    don't hit the network in unit tests.
    """
    assert callable(load_odac25)
    assert callable(min_h2o_binding_per_mof)


def test_min_h2o_binding_per_mof_on_synthetic_data() -> None:
    """Verify the per-MOF aggregation logic on a hand-built table."""
    df = pd.DataFrame(
        {
            "mof_id": ["A", "A", "A", "B", "B", "C", "C"],
            "adsorbate": ["H2O", "H2O", "CO2", "H2O", "H2O", "CO2", "H2O"],
            "ads_energy": [-0.5, -0.8, -1.2, -0.3, -0.1, -1.5, -0.7],
        }
    )
    out = min_h2o_binding_per_mof(df)
    # Index by MOF for easier assertions
    by_mof = out.set_index("mof_id")
    assert by_mof.loc["A", "min_h2o_binding_eV"] == -0.8
    assert by_mof.loc["A", "n_h2o_configurations"] == 2  # CO2 row excluded
    assert by_mof.loc["B", "min_h2o_binding_eV"] == -0.3
    assert by_mof.loc["B", "n_h2o_configurations"] == 2
    assert by_mof.loc["C", "min_h2o_binding_eV"] == -0.7
    assert by_mof.loc["C", "n_h2o_configurations"] == 1


def test_min_h2o_binding_per_mof_water_alias() -> None:
    """The aggregator accepts 'water' as well as 'H2O'."""
    df = pd.DataFrame(
        {
            "mof_id": ["A", "A"],
            "adsorbate": ["water", "Water"],
            "ads_energy": [-0.4, -0.9],
        }
    )
    out = min_h2o_binding_per_mof(df)
    assert out.loc[0, "min_h2o_binding_eV"] == -0.9
    assert out.loc[0, "n_h2o_configurations"] == 2


def test_min_h2o_binding_per_mof_forwards_defective_flag() -> None:
    """If the input table has a defective column, the output keeps it."""
    df = pd.DataFrame(
        {
            "mof_id": ["A", "A", "B"],
            "adsorbate": ["H2O", "H2O", "H2O"],
            "ads_energy": [-0.5, -0.7, -0.2],
            "defective": [True, True, False],
        }
    )
    out = min_h2o_binding_per_mof(df)
    by_mof = out.set_index("mof_id")
    assert bool(by_mof.loc["A", "defective"]) is True
    assert bool(by_mof.loc["B", "defective"]) is False
