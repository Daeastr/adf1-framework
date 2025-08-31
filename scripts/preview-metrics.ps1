# Force UTF-8 output every time
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Ensure orchestrator_artifacts exists
$logDir = "orchestrator_artifacts"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Run orchestrator with Gemini metrics instruction and capture output
$env:PYTHONIOENCODING = "utf-8"
$logFile = Join-Path $logDir "run.log"

python -m core.orchestrator instructions/preview-metrics.json |
    Tee-Object -FilePath $logFile -Encoding UTF8 | Out-Null

# Find newest log
$latestLog = Get-ChildItem -Path $logDir -Filter "*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $latestLog) {
    Write-Output "❌ No log files found in $logDir"
    exit 1
}

Write-Output "📄 Previewing: $($latestLog.Name)"
Write-Output ""

# Output log content exactly as-is
Get-Content $latestLog.FullName -Encoding UTF8 |
    ForEach-Object { Write-Output $_ }
