"""Train/validation/test splits for MOF datasets.

Random splits massively overstate performance on materials data because of
near-duplicate structures (same formula, slight structural variations). All
splits in this project are *cluster-based* or *composition-based*.

Phase 1+ work — placeholder. Plan:

- ``composition_split(df, test_frac, seed)``: group by chemical formula or
  reduced composition, then assign whole groups to splits.
- ``cluster_split(features, n_clusters, test_frac, seed)``: KMeans-cluster
  in feature space, assign whole clusters to splits.
- ``scaffold_split(...)``: more aggressive — group by topology / linker
  family. Bites harder, more honest evaluation.
"""

from __future__ import annotations

import pandas as pd


def composition_split(
    df: pd.DataFrame,
    test_frac: float = 0.2,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split ``df`` into (train, test) by chemical formula.

    Not yet implemented.
    """
    raise NotImplementedError("composition_split lands in Phase 1.")
