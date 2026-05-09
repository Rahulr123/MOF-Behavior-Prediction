"""Unit tests for ``mofwater.eval.metrics``."""

from __future__ import annotations

import math

import numpy as np

from mofwater.eval.metrics import mae, r2, rmse


def test_rmse_handles_lists() -> None:
    assert rmse([0, 0, 0], [1, 1, 1]) == 1.0


def test_mae_handles_negatives() -> None:
    assert mae([1, 2, 3], [-1, 0, 1]) == 2.0


def test_r2_constant_truth_is_nan() -> None:
    """R² is undefined when truth has zero variance; we return NaN."""
    result = r2([5, 5, 5], [5, 5, 5])
    assert math.isnan(result)


def test_r2_matches_sklearn_on_random_data() -> None:
    """Spot-check against sklearn to catch any sign/formula errors."""
    from sklearn.metrics import r2_score

    rng = np.random.default_rng(0)
    y = rng.normal(size=100)
    yhat = y + rng.normal(scale=0.5, size=100)
    assert math.isclose(r2(y, yhat), r2_score(y, yhat), rel_tol=1e-9)
