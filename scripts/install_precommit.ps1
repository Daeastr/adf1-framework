# Installs a git pre-commit hook that runs the instruction linter (scripts/check_instructions.py)
# This script is intended to be executed from the repository's scripts folder.

# Resolve repo root (parent of the scripts directory)
$repo = Resolve-Path ".." | Select-Object -ExpandProperty Path
$hookDir = Join-Path $repo ".git\hooks"
$hookFile = Join-Path $hookDir "pre-commit"

if (-not (Test-Path $hookDir)) {
    Write-Host "No .git/hooks directory found. Are you in a git repo?"
    exit 1
}

# Hook content: POSIX sh that invokes the Python instruction linter
$hookContent = @'
#!/bin/sh
# Auto-run instruction linter before commit
python scripts/check_instructions.py
rc=$?
if [ $rc -ne 0 ]; then
  echo "Instruction lint failed; aborting commit."
  exit $rc
fi
exit 0
'@

Set-Content -Path $hookFile -Value $hookContent -Encoding ASCII -Force

# Make executable if chmod is available (useful on Unix-like systems)
if (Get-Command chmod -ErrorAction SilentlyContinue) {
    & chmod +x $hookFile
}

Write-Host "Installed pre-commit hook at $hookFile"
