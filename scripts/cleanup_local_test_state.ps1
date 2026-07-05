$ErrorActionPreference = "Stop"

$roaming = [Environment]::GetFolderPath("ApplicationData")
$sendTo = Join-Path $roaming "Microsoft\Windows\SendTo"
$appState = Join-Path $roaming "WSAQuickDrop"
$targets = @(
    (Join-Path $appState "logs"),
    (Join-Path $appState "config.json"),
    (Join-Path $sendTo "WSA QuickDrop.bat"),
    (Join-Path $sendTo "WSA QuickDrop.lnk")
)

Write-Host "WSA QuickDrop local test-state cleanup"
Write-Host "This script only targets WSA QuickDrop logs, config, SendTo entries, and HKCU context-menu entries."
Write-Host "It will not remove ADB, Android SDK, WSA, Python, this project folder, or user-selected files."
Write-Host ""
Write-Host "Planned removals if present:"
foreach ($target in $targets) {
    Write-Host " - $target"
}
Write-Host " - HKCU\Software\Classes\*\shell\WSAQuickDrop"
Write-Host ""

$answer = Read-Host "Type DELETE to remove these items"
if ($answer -ne "DELETE") {
    Write-Host "Cancelled. Nothing was removed."
    exit 0
}

foreach ($target in $targets) {
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
        Write-Host "Removed $target"
    }
}

& reg.exe delete "HKCU\Software\Classes\*\shell\WSAQuickDrop" /f | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Removed HKCU context-menu entry."
} else {
    Write-Host "HKCU context-menu entry was not present."
}

Write-Host "Cleanup complete."
