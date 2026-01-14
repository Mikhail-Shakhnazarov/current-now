# Atlas TUI (3d_printed)

Standalone build under `repo copy/3d_printed/`.

Goals:
- Solid Textual TUI, dummy engine, and local Glass web inspector.
- Deterministic, testable artifacts (events/snapshots/logs) with a fast `unittest` smoke suite.

Run:
- With Textual installed: `PYTHONPATH=src python -m atlas_tui.cli --project-root . --repo-root <path-to-repo>`
- Using the repo copy venv: `..\.venv\Scripts\python.exe -m atlas_tui.cli --project-root . --repo-root <path-to-repo>`

Tests:
- `python -m unittest discover -s tests -v` (UI tests skip if `textual` is missing)
- `..\.venv\Scripts\python.exe -m unittest discover -s tests -v` (runs UI tests)
