"""Featurization of MOF structures and compositions.

Phase 1+ work — placeholder. Plan:

- ``compose_features(df)``: Magpie / matminer composition features from the
  ``formula`` column. Fast, structure-free, becomes the baseline featurizer.
- ``structural_features(df)``: pore-size distribution, surface area, void
  fraction (often already in QMOF columns; this just curates).
- ``rac_features(df)``: revised autocorrelation features (Heather Kulik group).
  Strong but install-pain (molSimplify); defer until needed.
- ``graph_features(df)``: convert structures to PyG ``Data`` objects for GNN
  models. Phase 3+.
"""

from __future__ import annotations

import pandas as pd


def compose_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute composition-based features from a DataFrame with a ``formula`` column.

    Not yet implemented. Will use ``matminer.featurizers.composition`` to
    produce Magpie-style features (mean/min/max/std of element properties).
    """
    raise NotImplementedError("compose_features lands in Phase 1.")
