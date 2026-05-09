# MOF Behavior Prediction

Machine learning models that predict water adsorption behavior of metal-organic frameworks (MOFs), with calibrated uncertainty and a stability filter, applied to candidate screening for atmospheric water harvesting.

## Scientific question

Given a MOF's structure and composition, can we predict its water adsorption isotherm (or summary properties of it — working capacity in a target relative-humidity window, step location, maximum uptake) accurately enough to rank candidates for atmospheric water harvesting? And, separately, how much do "top picks" change once we filter for hydrolytic stability?

This is a screening problem, not a discovery problem. The output of a successful project is a ranked list of MOFs with calibrated confidence intervals on their predicted water properties, plus a critical evaluation of which prior published "top MOFs" survive a consistent re-evaluation pipeline.

## Approach

1. **Data**: Start from the QMOF database (~20k MOFs with DFT-quality properties). Add CoREMOF water adsorption isotherm data where available.
2. **Featurization**: Composition-based features (matminer/Magpie) as the primary baseline; structure-aware GNN features as a secondary path.
3. **Models**: Random forest / gradient boosting baselines first; GNN models second; uncertainty via deep ensembles.
4. **Evaluation**: Cluster-based train/val/test splits, *not* random splits. Report calibrated uncertainty (90% interval coverage), not just point-prediction error.
5. **Stability filter**: Use a foundation MLIP (MACE-MP-0 or ORB-v2) to relax candidate structures and flag those that don't survive geometry optimization.
6. **Critical evaluation**: Apply the full pipeline to "top MOF" lists from prior published screening papers and report agreement / disagreement.

## Status

Currently: **Phase 0 — Infrastructure setup.** Repo scaffolded, dependencies installed, dataset loader skeleton in place. No models trained yet.

Next: Pull QMOF data, build EDA notebook, define eval splits.

See [`notes/logbook.md`](notes/logbook.md) for weekly progress entries.

## Reproducing

Requires Python 3.11+ and [`uv`](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/YOUR_USERNAME/MOF-Behavior-Prediction.git
cd MOF-Behavior-Prediction
uv sync                         # creates .venv and installs all deps from uv.lock
uv run scripts/build_dataset.py # downloads + caches the QMOF dataset
uv run pytest                   # run the test suite
```

Cached data lands in `data/` (gitignored). Run `python scripts/build_dataset.py --help` for options.

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

- DFT-level labels (not experiment), with all the systematic errors that come with that.
- Selection bias toward stable, simple MOFs in the training data.
- Synthesizability is not modeled directly.
- Stability filtering via foundation MLIP is a coarse proxy for real hydrolytic stability.

See [`notes/limitations.md`](notes/limitations.md) for a more thorough discussion (added once Phase 1 is complete).

## License

MIT — see [`LICENSE`](LICENSE).
