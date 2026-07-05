$ErrorActionPreference = "Stop"

$sendTo = Join-Path $env:APPDATA "Microsoft\Windows\SendTo"
$targets = @(
    (Join-Path $sendTo "WSA QuickDrop.bat"),
    (Join-Path $sendTo "WSA QuickDrop.lnk")
)

$removed = $false
foreach ($target in $targets) {
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Force
        Write-Host "Removed $target"
        $removed = $true
    }
}

if (-not $removed) {
    Write-Host "WSA QuickDrop SendTo entry was not installed."
}
