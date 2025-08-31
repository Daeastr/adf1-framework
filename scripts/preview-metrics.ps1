# Force UTF-8 output every time
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# --- CONFIG ---
$logDir = "orchestrator_artifacts"
$pythonPreview = "scripts/preview_metrics.py"  # We'll create this helper

# --- MODE 1: Replay from latest log ---
if (Test-Path $logDir) {
    $latestLog = Get-ChildItem -Path $logDir -Filter "*.log" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($latestLog) {
        Write-Output "📄 Previewing from log: $($latestLog.Name)"
        Write-Output ""
        Get-Content $latestLog.FullName -Encoding UTF8 | ForEach-Object { Write-Output $_ }
        exit 0
    }
}

# --- MODE 2: Live reporter output ---
if (Test-Path $pythonPreview) {
    Write-Output "⚡ No logs found — generating live preview via reporter..."
    python $pythonPreview
} else {
    Write-Output "❌ No logs found and no live preview script available."
}
