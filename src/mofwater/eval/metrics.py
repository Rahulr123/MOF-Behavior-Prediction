"""Point-prediction metrics.

Calibration metrics (ECE, sharpness, reliability diagrams) live in
``mofwater.eval.calibration``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def rmse(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Root mean squared error."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Mean absolute error."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def r2(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Coefficient of determination R²."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)
