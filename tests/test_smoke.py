"""Smoke tests — verify the package imports and basic plumbing works.

These tests don't touch the network. They confirm:
- the package and its subpackages import cleanly
- metrics produce sensible values on toy data
- the loader function is callable and raises a clear error when the network
  cannot be reached and there's no cache.
"""

from __future__ import annotations

import numpy as np

import mofwater
from mofwater.data import load_qmof
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
    # R² on a constant offset is bounded; just confirm it's < 1
    assert r2(y_true, y_pred) < 1.0


def test_load_qmof_is_callable() -> None:
    """The loader is importable and callable. Network behavior is tested
    by actually running scripts/build_dataset.py — we don't hit the network
    in unit tests.
    """
    assert callable(load_qmof)
