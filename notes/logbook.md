# Logbook

Weekly entries on what was tried, what was learned, and what's next. The point is to leave a reasoning trail — useful for the owner's own memory, for hiring conversations, and for any future contributor (human or AI) trying to understand why things are the way they are.

Format for each entry:
- **What I tried.** Concrete actions taken.
- **What I expected.** Hypothesis going in.
- **What happened.** Observations, including surprises.
- **What I learned.** Distilled takeaway.
- **Next.** What this week's work suggests should come next.

---

## Week 0 — Project setup (May 2026)

**What I tried.** Set up the project from scratch: cloned an empty GitHub repo, installed `uv` for Python package management, installed VS Code with the Python and Jupyter extensions, configured `git` and the GitHub CLI, initialized a packaged Python project with `uv init --package`, installed core dependencies (numpy, pandas, scikit-learn, matplotlib, pymatgen, matminer, plus dev tools), and wrote a smoke test confirming all imports work.

**What I expected.** That setup would be straightforward. (It mostly was, but a few small papercuts ate time — see below.)

**What happened.** Three notable hiccups: (1) `uv init --package mofwater` interpreted `mofwater` as a path and created a subdirectory; the right invocation is `uv init --package --name mofwater`. (2) Created `smoke_test.py` inside `src/mofwater/` instead of the repo root by right-clicking on the wrong VS Code panel — `find` recovered it. (3) `pymatgen` doesn't expose `__version__` at the top-level module; `importlib.metadata.version("pymatgen")` is the reliable way to query versions for any package. Beyond those, the rest went cleanly. Pushed initial commit to GitHub.

**What I learned.** Modern Python tooling (`uv`, `ruff`) is fast and pleasant once you know the idioms; the friction is almost entirely in the first hour of "where do I put files and how do I structure a project." VS Code's integrated terminal + Jupyter notebook view makes the editor/notebook dichotomy mostly disappear, which addresses most of the "but I'd rather use Colab" reflex. Also: `importlib.metadata.version` is the default I'll use everywhere going forward.

**Next.** Implement the QMOF data loader (`src/mofwater/data/load.py`), write a build script that runs it end-to-end, then a first EDA notebook to look at the property distributions and missingness patterns.

---

## Week 1 — Dataset pivot to ODAC23 (May 2026)

**What I tried.** Started building toward the QMOF database as the project's data source, with band gap (or eventually water-uptake property) as the regression target. Got the loader, build script, tests, and docs all in place pointing at QMOF.

**What I expected.** That QMOF was the natural starting point — it's the most commonly cited MOF property dataset, widely benchmarked, easy to consume as a CSV.

**What happened.** Stopped to ask "why this dataset?" and discovered the Open DAC 2023 (ODAC23) dataset from FAIR Chemistry + Georgia Tech. ODAC23 contains ~176k DFT adsorption energies of CO₂ and H₂O on ~8,400 MOFs — including defective variants, which essentially no other public MOF dataset includes. Critically, it has *actual water binding energies* as labels, while QMOF only has structural and electronic properties; predicting water uptake from QMOF would require either GCMC simulations on top or proxy features. ODAC also comes with pretrained foundation MLIPs (UMA, EquiformerV2, eSEN) trained on this exact data.

**What I learned.** "Use the standard dataset" is the safe pick, not necessarily the right one. For this project's question (water adsorption in MOFs), ODAC23 is a much tighter fit — the target is *in the data* rather than approximated from features. The cost is a heavier data infrastructure (LMDB files, the fairchem package, larger total size), but the scientific framing becomes substantially cleaner.

I also locked in the first regression target: **minimum H₂O binding energy per MOF** — the most-negative binding energy across all sampled H₂O configurations for that MOF. Single scalar per MOF, unambiguous label, useful as a screening primitive (strongly-binding MOFs are candidates for arid-region water harvesting; weakly-binding MOFs are interesting for direct air capture where water competes with CO₂). It's also a more honest first step than jumping straight to isotherm or working-capacity prediction, both of which require thermodynamic post-processing on top of the raw DFT labels.

**Next.** Rewrite the loader for ODAC23, update README/CLAUDE accordingly, write the first EDA notebook to characterize the per-MOF minimum H₂O binding energy distribution (range, outliers, coverage of pristine vs defective MOFs, missingness). Then decide on the MOF-level held-out split before computing any features.

---

<!-- Add new entries above this line. Most recent at top. -->
