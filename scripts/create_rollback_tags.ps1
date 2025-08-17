Param(
    [switch]$Push
)

Set-Location (Split-Path -Path $MyInvocation.MyCommand.Definition -Parent) | Out-Null
Set-Location ..  # repo root

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$layers = @('root','core','adf1-plan-preview','tests','instructions')

foreach ($layer in $layers) {
    $tag = "rollback-$layer-$ts"
    $existing = git tag -l $tag
    if ($existing) {
        Write-Host "Tag $tag already exists, skipping"
        continue
    }

    $sha = git rev-parse --verify HEAD
    $message = @()
    $message += "Rollback tag for layer: $layer"
    $message += "Timestamp: $ts"
    $message += "Commit: $sha"
    $message = $message -join "`n"

    git tag -a $tag -m $message
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create tag $tag" -ForegroundColor Red
    } else {
        Write-Host "Created tag $tag -> $sha"
    }
}

if ($Push) {
    git push origin --tags
    if ($LASTEXITCODE -eq 0) { Write-Host "Pushed tags to origin" } else { Write-Host "Failed to push tags" -ForegroundColor Red }
}
