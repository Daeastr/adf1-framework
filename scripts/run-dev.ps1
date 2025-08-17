# Run the VS Code Extension Development Host for the adf1-plan-preview extension
# Usage: Open PowerShell and run this script from the repo root:
#   .\scripts\run-dev.ps1

param()

$repoRoot = Resolve-Path "$PSScriptRoot\.."
$extPath = Join-Path $repoRoot 'adf1-plan-preview'
Write-Host "Launching Extension Development Host for: $extPath"

# Launch VS Code with the extension development path
# This opens a new VS Code window; press F5 in that window to start the Extension Development Host.
code --extensionDevelopmentPath "$extPath"

Write-Host "If the dev host opened, press F5 in the Extension Development Host to run the extension."
Write-Host "Once the dev host is running, open the Command Palette and run: 'Show AADF Plan Preview' or click the status bar button."
Write-Host "If 'code' is not in your PATH, add it from VS Code: Command Palette -> 'Shell Command: Install 'code' command in PATH'."
