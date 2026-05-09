"""Dataset loaders for MOF property databases.

Currently supported:
    - QMOF: ~20k MOFs with DFT-quality properties (Rosen et al., 2021).

Datasets are cached locally under ``data/raw/`` (gitignored). Subsequent
calls use the cache; pass ``force_download=True`` to re-fetch.
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

# QMOF metadata CSV. The QMOF project is hosted on Figshare; the file ID below
# may change when the dataset is updated. If the download fails, see
# https://github.com/arosen93/QMOF for the current download instructions and
# update QMOF_URL accordingly, or place the file manually at
# ``data/raw/qmof.csv``.
QMOF_URL = "https://figshare.com/ndownloader/files/41642951"
QMOF_FILENAME = "qmof.csv"


def load_qmof(
    data_dir: Path | str = "data",
    url: str = QMOF_URL,
    force_download: bool = False,
) -> pd.DataFrame:
    """Load the QMOF property database as a DataFrame.

    Parameters
    ----------
    data_dir
        Project data directory. The cached CSV lands at
        ``{data_dir}/raw/qmof.csv``.
    url
        URL to fetch the CSV from when no cache is present.
    force_download
        If True, re-download even if a cached copy exists.

    Returns
    -------
    pd.DataFrame
        QMOF property table with one row per MOF.

    Raises
    ------
    RuntimeError
        If the file cannot be downloaded *and* no manual cache exists.
    """
    data_dir = Path(data_dir)
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_path = raw_dir / QMOF_FILENAME

    if cache_path.exists() and not force_download:
        logger.info("Loading cached QMOF from %s", cache_path)
        return pd.read_csv(cache_path)

    logger.info("Downloading QMOF from %s -> %s", url, cache_path)
    try:
        _download_with_progress(url, cache_path)
    except (HTTPError, URLError, TimeoutError) as err:
        raise RuntimeError(
            f"Could not download QMOF from {url}.\n"
            f"Reason: {err}\n\n"
            "To fix this:\n"
            "  1. Check https://github.com/arosen93/QMOF for the current "
            "download URL.\n"
            "  2. Update QMOF_URL in src/mofwater/data/load.py, or\n"
            f"  3. Manually download the CSV and place it at {cache_path}."
        ) from err

    return pd.read_csv(cache_path)


def _download_with_progress(url: str, dest: Path, chunk_size: int = 8192) -> None:
    """Stream ``url`` to ``dest`` with a tqdm progress bar.

    Writes to a temporary file and renames on success so partial downloads
    don't poison the cache.
    """
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    request = Request(url, headers={"User-Agent": "mofwater/0.1"})
    with urlopen(request, timeout=60) as response:
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
