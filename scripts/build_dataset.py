"""Aggregate ODAC25 adsorption energies into a per-MOF summary CSV.

Usage:
    uv run scripts/build_dataset.py [--data-dir DIR]

Prerequisites:
    - data/raw/odac25_energies.csv must exist with columns
      mof_id, adsorbate, ads_energy. See src/mofwater/data/load.py for two
      ways to produce this file from ODAC25's native LMDB format.

After running:
    - {data-dir}/processed/odac25_min_h2o_per_mof.csv is written, with
      one row per MOF and the minimum H2O binding energy across configs.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from mofwater.data import (
    ODAC25_PROCESSED_FILENAME,
    load_odac25,
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

    # Step 1: load the configuration-level table.
    df = load_odac25(data_dir=args.data_dir)
    print(f"\nLoaded ODAC25 configurations: {len(df):,} rows")
    print(f"Columns: {list(df.columns)}")
    print("Adsorbate counts:")
    print(df["adsorbate"].value_counts().to_string())

    # Step 2: aggregate to per-MOF minimum H2O binding.
    processed_path = args.data_dir / "processed" / ODAC25_PROCESSED_FILENAME
    per_mof = min_h2o_binding_per_mof(df, save_to=processed_path)

    print(f"\nPer-MOF H2O summary: {len(per_mof):,} MOFs")
    print(per_mof.describe().to_string())
    print(f"\nWrote processed file to: {processed_path.resolve()}")


if __name__ == "__main__":
    main()
