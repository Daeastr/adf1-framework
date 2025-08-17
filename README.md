Developer notes
===============

Pre-commit hook: sync action map & generated placeholders
-------------------------------------------------------
This repository includes a local pre-commit hook that keeps `tests/action_map.json` in sync with the instruction docs and automatically scaffolds placeholder test files under `tests/__generated__/` so CI never fails with "file not found" for mapped tests.

How it works
- `scripts/sync_action_map.py` reads valid instruction documents (via `core.orchestrator.load_valid_instructions()`), updates `tests/action_map.json` with any missing action→test mappings, and writes minimal placeholder tests if a mapped test file is missing.
- `scripts/run_sync_action_map.py` is a small launcher that prefers the repo venv (`./venv` or `./.venv`) if present and re-executes the sync script with the correct interpreter. The pre-commit hook is configured to call this launcher.

Local setup
1. Activate your repo venv (optional but recommended):

   PowerShell:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install pre-commit
   pre-commit install
   ```

   Or, using pip in the active environment:
   ```powershell
   pip install pre-commit
   pre-commit install
   ```

2. From now on, commits will run the local hook which updates `tests/action_map.json` and creates placeholders under `tests/__generated__/` when needed.

Run manually
- To run the sync manually (without installing pre-commit):

  ```powershell
  python scripts/run_sync_action_map.py
  ```

Notes
- Placeholder tests are intentionally minimal (a single passing test). Remove or replace them with real tests as the codebase evolves.
- If you prefer placeholders in a different directory, update `scripts/sync_action_map.py` which controls the generated path.

