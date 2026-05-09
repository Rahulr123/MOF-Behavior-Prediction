"""Download and cache the QMOF property database.

Usage:
    uv run scripts/build_dataset.py [--force] [--data-dir DIR]

After running, the dataset CSV lands at ``{data-dir}/raw/qmof.csv``
(``data/raw/qmof.csv`` by default). Subsequent calls use the cache.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from mofwater.data.load import load_qmof


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

    df = load_qmof(data_dir=args.data_dir, force_download=args.force)

    print(f"\nLoaded QMOF: {len(df):,} rows, {len(df.columns)} columns")
    print(f"Cache location: {(args.data_dir / 'raw' / 'qmof.csv').resolve()}")
    print(f"\nFirst few columns: {list(df.columns[:8])}")
    print("\nDataFrame summary:")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()
