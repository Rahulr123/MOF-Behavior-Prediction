"""Loaders for the ODAC23 MOF adsorption-energy dataset.

ODAC23 (Open DAC 2023) is a collaboration between Meta FAIR and Georgia Tech.
It contains ~176k DFT adsorption-energy calculations for CO2 and H2O on
~8,400 MOFs (pristine and defective). The canonical reference is:

    Sriram et al., "The Open DAC 2023 Dataset and Challenges for Sorbent
    Discovery in Direct Air Capture," ACS Cent. Sci. 2024.
    https://pubs.acs.org/doi/10.1021/acscentsci.3c01629

This module loads the *configuration-level* energy table (one row per
(MOF, adsorbate, configuration)) and aggregates to a per-MOF summary
(one row per MOF, with the minimum H2O binding energy across configurations).

Data is cached locally under ``data/raw/`` and ``data/processed/``. Both are
gitignored; the build script regenerates them from scratch.

Notes on data acquisition
-------------------------
ODAC23 is hosted by the Open DAC project. The canonical entry point is
https://open-dac.github.io/ — they distribute the data via S3. The full
dataset (structures + energies) is hundreds of GB; for this project's first
phase we only need the adsorption-energy table, which is much smaller.

If the URL in ``ODAC23_ENERGIES_URL`` becomes stale (FAIR has been known
to reorganize their S3 layout when datasets update), the build script will
report a clear download failure and point you here for manual instructions.
You can then either:

1. Update ``ODAC23_ENERGIES_URL`` to a working URL and re-run the build, or
2. Manually download the energy table and place it at
   ``data/raw/odac23_energies.csv`` — the loader will pick it up from there.

Expected schema (case-insensitive column names accepted):
    - ``mof_id``         : str  -- MOF identifier (string token)
    - ``adsorbate``      : str  -- e.g. "H2O", "CO2", "CO2+H2O"
    - ``ads_energy``     : float -- adsorption energy in eV (more negative = stronger binding)
    - ``defective``      : bool (optional) -- pristine vs defective MOF
    - ``config_id``      : str (optional) -- configuration identifier
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)

# URL to the ODAC23 adsorption-energy table.
# This is a placeholder pointing at the public Open DAC project bucket. If it
# 404s, update it from https://open-dac.github.io/ and re-run the build.
ODAC23_ENERGIES_URL = (
    "https://dl.fbaipublicfiles.com/dac/odac23/odac23_adsorption_energies.csv"
)
ODAC23_FILENAME = "odac23_energies.csv"
ODAC23_PROCESSED_FILENAME = "odac23_min_h2o_per_mof.csv"

# Canonical column names we use internally. The loader normalizes incoming
# variants (lower-cased, underscored, common aliases) to these.
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


def load_odac23(
    data_dir: Path | str = "data",
    url: str = ODAC23_ENERGIES_URL,
    force_download: bool = False,
) -> pd.DataFrame:
    """Load the ODAC23 configuration-level adsorption-energy table.

    Returns one row per (MOF, adsorbate, configuration). Columns are normalized
    to ``mof_id``, ``adsorbate``, ``ads_energy`` (and optionally ``defective``,
    ``config_id``); see module docstring for the full schema.

    Parameters
    ----------
    data_dir
        Project data directory. The cached CSV lands at
        ``{data_dir}/raw/odac23_energies.csv``.
    url
        URL to fetch the CSV from when no cache is present.
    force_download
        If True, re-download even if a cached copy exists.

    Returns
    -------
    pd.DataFrame
        Configuration-level energy table.

    Raises
    ------
    RuntimeError
        If the file cannot be downloaded *and* no manual cache exists.
    """
    data_dir = Path(data_dir)
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_path = raw_dir / ODAC23_FILENAME

    if not cache_path.exists() or force_download:
        logger.info("Downloading ODAC23 energies from %s -> %s", url, cache_path)
        try:
            _download_with_progress(url, cache_path)
        except (HTTPError, URLError, TimeoutError) as err:
            raise RuntimeError(
                f"Could not download ODAC23 energies from {url}.\n"
                f"Reason: {err}\n\n"
                "To fix this:\n"
                "  1. Check https://open-dac.github.io/ for the current "
                "download location.\n"
                "  2. Update ODAC23_ENERGIES_URL in "
                "src/mofwater/data/load.py, or\n"
                f"  3. Manually download the CSV and place it at {cache_path}\n"
                "     (it must contain mof_id, adsorbate, and ads_energy "
                "columns — see module docstring for the full schema)."
            ) from err
    else:
        logger.info("Loading cached ODAC23 energies from %s", cache_path)

    df = pd.read_csv(cache_path)
    df = _normalize_columns(df)
    _validate_schema(df)
    return df


def min_h2o_binding_per_mof(
    df: pd.DataFrame,
    save_to: Path | str | None = None,
) -> pd.DataFrame:
    """Aggregate the ODAC23 configuration table to per-MOF minimum H2O binding.

    For each MOF, find the most-negative ``ads_energy`` across all
    configurations where ``adsorbate`` indicates water (case-insensitive match
    against "H2O", "h2o", "water").

    Parameters
    ----------
    df
        Configuration-level energy table from :func:`load_odac23`.
    save_to
        Optional path to write the resulting DataFrame as CSV.

    Returns
    -------
    pd.DataFrame
        One row per MOF, with columns:
            - ``mof_id``
            - ``min_h2o_binding_eV``: most negative H2O ads_energy
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
    # given MOF is either pristine or defective consistently in ODAC23).
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
    """Lower-case + alias-normalize column names in place-ish."""
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
            f"ODAC23 table is missing required columns: {sorted(missing)}.\n"
            f"Got columns: {sorted(df.columns)}.\n"
            "Add alias entries to COLUMN_ALIASES in load.py if the source "
            "data uses different names."
        )


def _download_with_progress(url: str, dest: Path, chunk_size: int = 8192) -> None:
    """Stream ``url`` to ``dest`` with a tqdm progress bar.

    Writes to a temporary file and renames on success so partial downloads
    don't poison the cache.
    """
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    request = Request(url, headers={"User-Agent": "mofwater/0.1"})
    with urlopen(request, timeout=120) as response:
        total = int(response.headers.get("Content-Length", 0))
        with open(tmp, "wb") as fh, tqdm(
            total=total or None,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=dest.name,
        ) as pbar:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                fh.write(chunk)
                pbar.update(len(chunk))
    shutil.move(str(tmp), str(dest))
