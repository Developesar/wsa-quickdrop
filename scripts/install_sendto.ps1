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
$sendTo = Join-Path $env:APPDATA "Microsoft\Windows\SendTo"
New-Item -ItemType Directory -Force -Path $sendTo | Out-Null
$batchPath = Join-Path $sendTo "WSA QuickDrop.bat"
$content = @"
@echo off
setlocal
"$exe" --send %*
exit /b %ERRORLEVEL%
"@
Set-Content -LiteralPath $batchPath -Value $content -Encoding ASCII
Write-Host "Installed SendTo launcher:"
Write-Host $batchPath
