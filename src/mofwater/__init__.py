"""mofwater — ML models for MOF water-adsorption property prediction.

Top-level package. See README.md and CLAUDE.md for project framing.

Subpackages
-----------
data  : dataset loaders, featurizers, train/val/test splits
models: baselines, GNNs, ensembling
eval  : metrics, calibration diagnostics
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mofwater")
except PackageNotFoundError:  # package is not installed
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
