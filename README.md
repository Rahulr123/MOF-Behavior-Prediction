# MOF Behavior Prediction

Machine learning models that predict water adsorption behavior in metal-organic frameworks (MOFs), with calibrated uncertainty, applied to candidate screening for atmospheric water harvesting and direct air capture.

## Scientific question

For a given MOF, **what is the minimum water binding energy across all considered H₂O configurations** — i.e., how strongly does the framework bind water at its best site? This is a single, well-defined scalar per MOF, derived from the Open DAC 2025 (ODAC25) dataset (Meta FAIR + Georgia Tech), and a sensible *first* regression target before tackling full isotherms or working capacities.

Predicting min H₂O binding energy is a useful screening primitive on its own:

- Strongly negative values flag MOFs that bind water tightly — desirable for arid-condition atmospheric water harvesting (high uptake at low RH) but potentially undesirable for direct air capture (water competes with CO₂).
- The opposite end of the distribution flags hydrophobic MOFs that resist water — interesting for DAC.
- It's a single number per MOF, so the prediction task and its eval are unambiguous.

Later phases of the project layer thermodynamic post-processing on top of binding-energy predictions to recover working-capacity and isotherm-summary properties.

## Approach

1. **Data**: ODAC25 — ~70 million DFT single-point calculations across ~15,000 MOFs (pristine, defective, functionalized, and synthetically generated frameworks) with CO₂, H₂O, N₂, and O₂ adsorbates. We use the H₂O subset and aggregate to the per-MOF minimum binding energy. ODAC25 supersedes the now-deprecated ODAC23 — see `notes/logbook.md` for the migration decision.
2. **Featurization**: Composition-based features (matminer / Magpie) as the baseline; structure-aware features (RACs, then GNN embeddings) as secondary paths. ODAC25 ships structures as ASE-DB-compatible LMDB files, so structure features are available without separate downloads.
3. **Models**: Random forest / gradient boosting baselines first; GNN models second; uncertainty via deep ensembles.
4. **Evaluation**: MOF-level held-out splits (not random configuration splits). Cluster-based or composition-based train/val/test partitions. Report calibrated uncertainty (90% interval coverage), not just point-prediction error.
5. **Foundation-model comparison**: Use a pretrained ODAC25 MLIP (UMA, eSEN, or EquiformerV2) via the `FAIRChemCalculator` with task name `"odac"` to predict binding energies directly. Compare our trained-from-features models against this foundation-model baseline.
6. **Critical evaluation**: Re-evaluate "top MOFs" from prior published water-MOF screening papers under our consistent pipeline.

## Status

Currently: **Phase 0 — Infrastructure setup.** Repo scaffolded, dependencies installed, dataset loader skeleton in place for ODAC25. No data downloaded or models trained yet.

Next: Obtain ODAC25 H₂O adsorption energies (via `fairchem-data-odac` or HuggingFace), EDA on binding-energy distributions, decide on splits, baseline model.

See [`notes/logbook.md`](notes/logbook.md) for weekly progress entries.

## Reproducing

Requires Python 3.11+ and [`uv`](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/YOUR_USERNAME/MOF-Behavior-Prediction.git
cd MOF-Behavior-Prediction
uv sync                         # creates .venv and installs all deps from uv.lock
uv run scripts/build_dataset.py # aggregates the ODAC25 H2O adsorption energies
uv run pytest                   # run the test suite
```

Cached data lands in `data/` (gitignored). Run `python scripts/build_dataset.py --help` for options.

### Obtaining ODAC25

ODAC25 is distributed as ASE-DB-compatible LMDB files (`.aselmdb`). Two paths to get the per-configuration H₂O adsorption energies into the CSV that `build_dataset.py` expects at `data/raw/odac25_energies.csv`:

1. **Via `fairchem-data-odac`** (official, heavyweight): `uv add fairchem-core fairchem-data-odac`, then iterate over the LMDB with `LmdbDataset({"src": "..."})` and extract energies. See [fair-chem.github.io/dac/datasets/odac25.html](https://fair-chem.github.io/dac/datasets/odac25.html).

2. **Via HuggingFace** (lighter, depending on what they publish): the dataset is at [huggingface.co/facebook/ODAC25](https://huggingface.co/facebook/ODAC25). If a tabular adsorption-energy file is published there, download it directly and rename to match our expected schema.

Either way, the resulting CSV must have columns `mof_id`, `adsorbate`, `ads_energy` (eV); the loader handles common alias variants automatically. See `src/mofwater/data/load.py` docstring for the full expected schema.

## Repo layout

```
src/mofwater/        # the actual Python package — all reusable code
  data/              # data loading, featurization, splits
  models/            # baselines, GNNs, ensembles
  eval/              # metrics, calibration
scripts/             # CLI entry points (thin wrappers over the package)
configs/             # YAML configs for runs
notebooks/           # exploration only — code lives in src/
tests/               # pytest tests
notes/               # logbook + design docs
data/                # raw + processed data (gitignored)
outputs/             # checkpoints, plots, run artifacts (gitignored)
```

## Limitations and honest caveats

This project is a learning vehicle and a portfolio piece, not a production system. Expect:

- ODAC25 binding energies are computed at the PBE+D3 level (with several improvements over ODAC23: corrected k-point sampling, re-relaxation of bare MOFs to account for adsorbate-induced deformation). PBE has known systematic errors for dispersion-dominated systems; D3 helps but isn't perfect for water in confined pores. Treat DFT labels as ground truth *only* relative to other DFT-PBE-D3 calculations.
- ODAC25's selection of MOFs is biased toward direct-air-capture relevance — generalization to MOFs outside this distribution is an open question and part of what the eval suite is meant to probe. It does include synthetically generated frameworks, which broadens the chemistry space beyond what's in CoREMOF/CSD.
- "Minimum binding energy per MOF" is a property of the sampled configurations — undersampling means we may not have found the true global minimum. We'll document our sensitivity to configuration count in the eval phase.
- Synthesizability is not modeled directly. Many ODAC25 MOFs (especially defective and synthetically generated variants) may not be realistically achievable.

See [`notes/limitations.md`](notes/limitations.md) for a more thorough discussion (added once Phase 1 is complete).

## References

- [The Open DAC 2025 Dataset (arXiv 2508.03162)](https://arxiv.org/abs/2508.03162) — primary reference for ODAC25
- [ODAC25 dataset docs (fair-chem.github.io)](https://fair-chem.github.io/dac/datasets/odac25.html)
- [facebook/ODAC25 on HuggingFace](https://huggingface.co/facebook/ODAC25)
- [The Open DAC 2023 Dataset (ACS Cent. Sci. 2024)](https://pubs.acs.org/doi/10.1021/acscentsci.3c01629) — historical reference (ODAC23 is now deprecated)
- [OpenDAC project page](https://open-dac.github.io/)
- [fairchem GitHub](https://github.com/facebookresearch/fairchem)
- [fairchem-data-odac package](https://github.com/facebookresearch/fairchem/tree/main/packages/fairchem-data-odac)

## License

MIT — see [`LICENSE`](LICENSE).
