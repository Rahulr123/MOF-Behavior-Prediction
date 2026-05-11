"""Download ODAC23 adsorption energies and produce a per-MOF summary.

Usage:
    uv run scripts/build_dataset.py [--force] [--data-dir DIR]

After running, two files exist:
    - {data-dir}/raw/odac23_energies.csv         (raw configuration-level)
    - {data-dir}/processed/odac23_min_h2o_per_mof.csv  (per-MOF minimum H2O binding)

The processed file is what downstream featurization and training scripts consume.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from mofwater.data import (
    ODAC23_PROCESSED_FILENAME,
    load_odac23,
    min_h2o_binding_per_mof,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Project data directory (default: ./data)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if a cached copy exists.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable info-level logging.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Step 1: load (downloading if needed) the configuration-level table.
    df = load_odac23(data_dir=args.data_dir, force_download=args.force)
    print(f"\nLoaded ODAC23 configurations: {len(df):,} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"Adsorbate counts:")
    print(df["adsorbate"].value_counts().to_string())

    # Step 2: aggregate to per-MOF minimum H2O binding.
    processed_path = args.data_dir / "processed" / ODAC23_PROCESSED_FILENAME
    per_mof = min_h2o_binding_per_mof(df, save_to=processed_path)

    print(f"\nPer-MOF H2O summary: {len(per_mof):,} MOFs")
    print(per_mof.describe().to_string())
    print(f"\nWrote processed file to: {processed_path.resolve()}")


if __name__ == "__main__":
    main()
