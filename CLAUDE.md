# CLAUDE.md

Instructions and context for Claude (or any agent) working on this repository.

## Project context

This is a side project at the intersection of materials engineering and ML. The owner (Rahul) is a materials engineer learning ML/AI, with a background in MOFs for atmospheric water harvesting. The project is intended as a portfolio piece for AI-for-science roles (Lila Sciences, Radical AI, Periodic Labs, Orbital Materials, etc.) and as a structured way to learn modern ML methods for materials.

The scientific framing, scope, and rationale are in [`README.md`](README.md). Read that first.

## Working agreements

**The repo is the source of truth.** When updating project state, update `notes/logbook.md` and the "Status" section of the README. Don't rely on chat-session memory.

**Notebooks are for exploration, not for production code.** Reusable functions go in `src/mofwater/`. Notebooks import from the package. If a function gets used in two notebooks, that's the trigger to extract it.

**Splits matter more than models.** Random splits of materials data dramatically overstate performance because of near-duplicate structures. Use cluster-based or composition-based splits and document them clearly.

**Uncertainty quantification is required, not optional.** Every property prediction must come with a calibrated uncertainty estimate. Reliability diagrams (predicted vs empirical coverage) belong in the eval suite.

**Baselines first.** A random forest on Magpie features must be benchmarked before any deep model. If the deep model doesn't beat that baseline on a held-out cluster split, the deep model isn't an improvement, regardless of what it does on a random split.

**Logbook discipline.** Weekly entries in `notes/logbook.md`: what was tried, what was expected, what happened, what's next. This is for the owner's reasoning trail and for hiring conversations.

## Conventions

- Python 3.11. Package manager is `uv`. No `pip install` directly.
- Format and lint with `ruff`. Run `uv run ruff format .` before committing.
- Type hints on all public functions in `src/`. Internal helpers can skip them.
- Tests with `pytest`. New modules in `src/` should have a corresponding test file.
- Configs live in `configs/*.yaml`. Scripts take a `--config` flag.
- Plots go to `outputs/figures/`. Models go to `outputs/checkpoints/`. Both gitignored.
- Logs are JSON or CSV in `outputs/logs/`. No experiment tracker yet — keep it simple.
- Random seeds: every script that has randomness must accept `--seed` and default to 42.

## Where things live

```
src/mofwater/
  data/load.py        QMOF / CoREMOF download and caching
  data/featurize.py   composition + structural featurizers
  data/splits.py      cluster-based train/val/test splits
  models/baselines.py RF, XGBoost wrappers
  models/gnn.py       GNN model class (Phase 3+)
  eval/metrics.py     RMSE, MAE, R², per-cluster breakdowns
  eval/calibration.py reliability diagrams, ECE, sharpness
scripts/
  build_dataset.py    one-shot data download + cache
  train_baseline.py   train baseline given a config
  evaluate.py         run a model against the eval suite
configs/
  baseline_rf.yaml    starter random forest config
notes/
  logbook.md          weekly entries
  limitations.md      honest caveats (created once Phase 1 lands)
tests/
  test_*.py           one test file per module under test
```

## Current phase

**Phase 0 — Infrastructure setup.** Repo scaffolded, dependencies installed via uv. Dataset loader skeleton in place but data not yet downloaded.

**Next phase — Phase 1: Data and EDA.** Run the QMOF loader, explore property distributions, identify the water-adsorption-relevant subset, decide on split strategy, write up findings as the first real logbook entry.

When in doubt about scope, *narrow the scope*. This project is high-quality work on a well-defined slice, not a survey of the whole field.

## Useful commands

```bash
uv sync                                  # install / update deps
uv run scripts/build_dataset.py          # download QMOF
uv run pytest                            # run tests
uv run ruff format .                     # format code
uv run ruff check .                      # lint code
uv run python -c "import mofwater"       # sanity-check import
```

## Things to avoid

- Adding new dependencies without thinking. Each dep is a maintenance cost.
- Hyper-parameter tuning before the eval pipeline is solid. You'll fool yourself.
- Random splits. Always cluster splits.
- Reporting only point-prediction metrics. Always report calibration too.
- Notebooks with copy-pasted code from other notebooks. Extract to `src/`.
- Committing data files, model checkpoints, or `.venv/`. The gitignore covers these — verify before committing.
