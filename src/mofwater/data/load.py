"""Loaders for the ODAC25 MOF adsorption-energy dataset.

ODAC25 (Open DAC 2025) is a collaboration between Meta FAIR and Georgia Tech.
It contains ~70 million DFT single-point calculations for CO2, H2O, N2, and
O2 adsorption across ~15,000 MOFs (pristine, defective, functionalized, and
synthetically generated). It supersedes the now-deprecated ODAC23. Canonical
references:

    Sriram et al., "The Open DAC 2025 Dataset for Sorbent Discovery in
    Direct Air Capture," arXiv 2508.03162, 2025.
    https://arxiv.org/abs/2508.03162

    Dataset docs: https://fair-chem.github.io/dac/datasets/odac25.html
    HuggingFace: https://huggingface.co/facebook/ODAC25
    Python package: https://github.com/facebookresearch/fairchem/
                    tree/main/packages/fairchem-data-odac

This module loads the *configuration-level* adsorption-energy table (one row
per (MOF, adsorbate, configuration)) and aggregates to a per-MOF summary
(one row per MOF, with the minimum H2O binding energy across configurations).

Obtaining ODAC25
----------------
ODAC25 is distributed as ASE-DB-compatible LMDB files (``*.aselmdb``). This
loader doesn't read LMDB directly — it expects a normalized CSV at
``data/raw/odac25_energies.csv`` with columns ``mof_id``, ``adsorbate``,
``ads_energy`` (plus optional ``defective``, ``config_id``).

Two paths to produce that CSV:

1. **Via fairchem-data-odac** (official, heavy install):

   .. code-block:: bash

       uv add fairchem-core fairchem-data-odac
       # then write a small script that iterates an LMDB file:

   .. code-block:: python

       from fairchem.core.datasets import LmdbDataset
       ds = LmdbDataset({"src": "path/to/odac25_train.aselmdb"})
       # ds[i] yields ASE Atoms-like objects with energy, forces, adsorbate
       # info — collect into a DataFrame and write to data/raw/odac25_energies.csv

2. **Via HuggingFace** (potentially lighter, depending on file layout):

   .. code-block:: bash

       uv add huggingface_hub datasets

   Then download from ``facebook/ODAC25`` and convert. The exact files
   available on the HF page should be inspected manually.

Either way, the resulting CSV must conform to the expected schema below.

Expected CSV schema
-------------------
Required columns (case-insensitive; common aliases are normalized):
    - ``mof_id``    : str   -- MOF identifier
    - ``adsorbate`` : str   -- e.g. "H2O", "CO2", "CO2+H2O"
    - ``ads_energy``: float -- adsorption energy in eV (more negative = stronger binding)

Optional columns (forwarded if present):
    - ``defective`` : bool  -- pristine vs defective MOF
    - ``config_id`` : str   -- configuration identifier
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ODAC25_FILENAME = "odac25_energies.csv"
ODAC25_PROCESSED_FILENAME = "odac25_min_h2o_per_mof.csv"

# Canonical column names. Incoming variants are normalized to these.
COL_MOF = "mof_id"
COL_ADSORBATE = "adsorbate"
COL_ENERGY = "ads_energy"
COL_DEFECTIVE = "defective"
COL_CONFIG = "config_id"

# Aliases that get mapped to canonical column names during normalization.
COLUMN_ALIASES: dict[str, str] = {
    "mof": COL_MOF,
    "mof_name": COL_MOF,
    "system_id": COL_MOF,
    "ads": COL_ADSORBATE,
    "adsorbate_type": COL_ADSORBATE,
    "adsorbates": COL_ADSORBATE,
    "energy": COL_ENERGY,
    "energy_ev": COL_ENERGY,
    "adsorption_energy": COL_ENERGY,
    "ads_energy_ev": COL_ENERGY,
    "is_defective": COL_DEFECTIVE,
    "defect": COL_DEFECTIVE,
    "config": COL_CONFIG,
    "configuration": COL_CONFIG,
    "configuration_id": COL_CONFIG,
}


def load_odac25(data_dir: Path | str = "data") -> pd.DataFrame:
    """Load the ODAC25 configuration-level adsorption-energy table.

    Reads ``{data_dir}/raw/odac25_energies.csv``, normalizes column names,
    validates the schema, and returns the DataFrame.

    Parameters
    ----------
    data_dir
        Project data directory. The CSV must already exist at
        ``{data_dir}/raw/odac25_energies.csv``. See the module docstring
        for how to produce this file from ODAC25's native LMDB format.

    Returns
    -------
    pd.DataFrame
        One row per (MOF, adsorbate, configuration).

    Raises
    ------
    FileNotFoundError
        If the CSV does not exist. The error message points to the module
        docstring for instructions on producing it.
    ValueError
        If the CSV is missing required columns.
    """
    data_dir = Path(data_dir)
    csv_path = data_dir / "raw" / ODAC25_FILENAME

    if not csv_path.exists():
        raise FileNotFoundError(
            f"ODAC25 energies CSV not found at {csv_path}.\n\n"
            "This loader expects a normalized CSV produced from ODAC25's "
            "native LMDB format. See the module docstring in "
            "src/mofwater/data/load.py for two paths to produce it:\n"
            "  1. Via fairchem-data-odac (official)\n"
            "  2. Via HuggingFace facebook/ODAC25\n\n"
            "Required columns: mof_id, adsorbate, ads_energy.\n"
            "Optional: defective, config_id."
        )

    logger.info("Loading ODAC25 energies from %s", csv_path)
    df = pd.read_csv(csv_path)
    df = _normalize_columns(df)
    _validate_schema(df)
    return df


def min_h2o_binding_per_mof(
    df: pd.DataFrame,
    save_to: Path | str | None = None,
) -> pd.DataFrame:
    """Aggregate the configuration table to per-MOF minimum H2O binding.

    For each MOF, find the most-negative ``ads_energy`` across all
    configurations where ``adsorbate`` indicates water (case-insensitive
    match against "H2O", "h2o", "water").

    Parameters
    ----------
    df
        Configuration-level energy table from :func:`load_odac25`.
    save_to
        Optional path to write the resulting DataFrame as CSV.

    Returns
    -------
    pd.DataFrame
        One row per MOF, with columns:
            - ``mof_id``
            - ``min_h2o_binding_eV``: most-negative H2O ads_energy
            - ``n_h2o_configurations``: count of H2O configurations sampled
            - ``defective``: forwarded if present in source

    Raises
    ------
    ValueError
        If no H2O rows are present in the input.
    """
    h2o_mask = df[COL_ADSORBATE].astype(str).str.lower().isin({"h2o", "water"})
    h2o = df.loc[h2o_mask].copy()
    if h2o.empty:
        raise ValueError(
            "No H2O rows found in the input. Check that the adsorbate column "
            "contains values like 'H2O' or 'water'."
        )

    group = h2o.groupby(COL_MOF, as_index=False)
    agg = group.agg(
        min_h2o_binding_eV=(COL_ENERGY, "min"),
        n_h2o_configurations=(COL_ENERGY, "count"),
    )

    # Forward the defective flag if present (take 'any' across configs — a
    # given MOF is either pristine or defective consistently in ODAC25).
    if COL_DEFECTIVE in h2o.columns:
        defect_per_mof = group[COL_DEFECTIVE].agg(lambda s: bool(s.any()))
        agg = agg.merge(defect_per_mof, on=COL_MOF, how="left")

    if save_to is not None:
        save_to = Path(save_to)
        save_to.parent.mkdir(parents=True, exist_ok=True)
        agg.to_csv(save_to, index=False)
        logger.info("Wrote per-MOF minimum H2O binding table to %s", save_to)

    return agg


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case + alias-normalize column names."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns=COLUMN_ALIASES)
    return df


def _validate_schema(df: pd.DataFrame) -> None:
    """Raise a clear error if required columns are missing."""
    required = {COL_MOF, COL_ADSORBATE, COL_ENERGY}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"ODAC25 table is missing required columns: {sorted(missing)}.\n"
            f"Got columns: {sorted(df.columns)}.\n"
            "Add alias entries to COLUMN_ALIASES in load.py if the source "
            "data uses different names."
        )
