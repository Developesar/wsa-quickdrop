$ErrorActionPreference = "Stop"

$baseKey = "HKCU\Software\Classes\*\shell\WSAQuickDrop"
& reg.exe delete $baseKey /f | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Removed optional HKCU context menu item."
} else {
    Write-Host "WSA QuickDrop context menu item was not installed."
}
