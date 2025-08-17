Contributing Guide
==================

This file documents developer setup and the repository's small developer tooling (pre-commit hook and action→test sync workflow).

Quick start
-----------
1. Create and activate a Python virtual environment in the repo root (recommended):

   PowerShell (Windows):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install --upgrade pip
   ```

   macOS / Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```

2. Install developer dependencies (optional but recommended):

   ```bash
   pip install -r requirements.txt
   # if you don't have requirements, at least install pre-commit and pytest
   pip install pre-commit pytest
   ```

Testing locally
---------------
- Run the full test suite with pytest:

  ```bash
  pytest -q
  ```

Pre-commit hook: sync action map & generate placeholders
------------------------------------------------------
This project includes a local pre-commit hook that keeps `tests/action_map.json` in sync with valid instruction docs and scaffolds placeholder tests under `tests/__generated__/` when a mapped test file is missing.

Files involved:
- `scripts/sync_action_map.py` — the sync script that updates the JSON mapping and writes placeholder tests.
- `scripts/run_sync_action_map.py` — a small launcher that attempts to use the repository venv's Python interpreter (if present) and runs the sync script.
- `.pre-commit-config.yaml` — registers a local pre-commit hook that calls the launcher.

Install the hook (recommended):
1. Ensure your venv is activated (see Quick start).
2. Install pre-commit into your environment:

   ```powershell
   pip install pre-commit
   pre-commit install
   ```

3. The next commit will automatically run the sync hook. To run it manually now:

   ```powershell
   python scripts/run_sync_action_map.py
   ```

Notes about the launcher
- The launcher will prefer the repo venv if it detects `./venv` or `./.venv` and will re-execute using that interpreter so the sync script uses the same environment as you.
- If no venv is found, the launcher runs the sync script in-process using the current interpreter.

Placeholders
- Placeholder tests are written to `tests/__generated__/test_<action>.py` and contain a single passing test named `test_placeholder_for_<action>`.
- Replace generated placeholders with real tests as you implement behavior.

Extension development (Plan Preview)
-----------------------------------
The VS Code extension for Plan Preview is in `adf1-plan-preview/`.
- To develop the extension locally, open the folder in VS Code and run "Launch Extension" (or use the provided `scripts/run-dev.ps1` helper on Windows).
- The extension registers a command `AADF: Show Plan Preview` and a status item `Plan Preview` which opens the webview.
- The command `aadf1.selectiveRerun` will open an integrated terminal and run the sync script followed by `pytest` (optionally with a `-k` filter). This flows through the `scripts/sync_action_map.py` sync pipeline so mapping is up-to-date before tests run.

Commit conventions
------------------
- Use conventional commit-style messages for clarity (e.g., `fix(...)`, `chore(...)`, `feat(...)`, `docs(...)`).

If anything in this guide is unclear or you want the hooks to behave differently (e.g., place placeholders in another folder), open a PR with the suggested change and I can update the scripts accordingly.
