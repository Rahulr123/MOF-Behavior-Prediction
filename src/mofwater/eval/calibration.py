"""Calibration metrics and reliability diagrams.

Phase 2+ work — placeholder. Plan:

- ``coverage_curve(y_true, y_mean, y_std)``: predicted-vs-empirical coverage
  for a Gaussian assumption (or quantile-based intervals).
- ``ece(y_true, y_mean, y_std)``: expected calibration error.
- ``sharpness(y_std)``: average interval width (lower is sharper).
- ``reliability_plot(...)``: matplotlib figure for inclusion in reports.
"""

from __future__ import annotations
