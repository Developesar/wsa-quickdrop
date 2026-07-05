param(
    [string]$ExePath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-QuickDropExecutable {
    param([string]$Candidate)

    if ($Candidate -and (Test-Path -LiteralPath $Candidate)) {
        return (Resolve-Path -LiteralPath $Candidate).Path
    }

    $candidates = @(
        (Join-Path $PSScriptRoot "WSAQuickDrop.exe"),
        (Join-Path $PSScriptRoot "..\WSAQuickDrop.exe"),
        (Join-Path $PSScriptRoot "..\dist\WSAQuickDrop.exe"),
        (Join-Path $PSScriptRoot "..\release\WSAQuickDrop-v0.1.0-win-x64\WSAQuickDrop.exe")
    )

    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path) {
            return (Resolve-Path -LiteralPath $path).Path
        }
    }

    throw "WSAQuickDrop.exe was not found. Pass -ExePath 'C:\path\to\WSAQuickDrop.exe'."
}

$exe = Resolve-QuickDropExecutable -Candidate $ExePath
$baseKey = "HKCU\Software\Classes\*\shell\WSAQuickDrop"
$commandKey = "$baseKey\command"
& reg.exe add $baseKey /ve /d "Send to WSA QuickDrop" /f | Out-Null
& reg.exe add $baseKey /v Icon /d "$exe" /f | Out-Null
& reg.exe add $commandKey /ve /d "`"$exe`" --send `"%1`"" /f | Out-Null
Write-Host "Installed optional HKCU context menu item."
Write-Host "SendTo remains recommended for reliable multi-file selection."
