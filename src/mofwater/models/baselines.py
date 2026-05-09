"""Baseline regression models — random forest, gradient boosting, ridge.

Phase 2 work — placeholder. The baseline must beat the trivial mean predictor
and serve as the floor every fancier model has to clear.

Plan:
- ``RandomForestBaseline``: thin wrapper over sklearn with sensible defaults
  (n_estimators=500, max_features='sqrt', n_jobs=-1).
- ``GradientBoostingBaseline``: XGBoost with early stopping.
- ``EnsembleRegressor``: deep ensemble of N baselines for uncertainty.
"""

from __future__ import annotations
