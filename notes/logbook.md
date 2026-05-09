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

<!-- Add new entries above this line. Most recent at top. -->
