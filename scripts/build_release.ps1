$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$python = (Get-Command python -ErrorAction Stop).Source
$venv = Join-Path $root ".venv"
$venvPython = Join-Path $venv "Scripts\python.exe"

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Invoke-Checked $python @("-m", "venv", $venv)
}

$env:PIP_CACHE_DIR = Join-Path $root ".pip-cache"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $root ".pyinstaller-cache"
Invoke-Checked $venvPython @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked $venvPython @("-m", "pip", "install", "-r", (Join-Path $root "requirements-dev.txt"))
Invoke-Checked $venvPython @("-m", "pytest", (Join-Path $root "src\WSAQuickDrop.Tests"))
Invoke-Checked $venvPython @("-m", "compileall", (Join-Path $root "src\WSAQuickDrop"))

$dist = Join-Path $root "dist"
$build = Join-Path $root "build"
if (Test-Path -LiteralPath $dist) {
    Remove-Item -LiteralPath $dist -Recurse -Force
}
if (Test-Path -LiteralPath $build) {
    Remove-Item -LiteralPath $build -Recurse -Force
}

Invoke-Checked $venvPython @(
    "-m", "PyInstaller",
    "--clean",
    "--onefile",
    "--name", "WSAQuickDrop",
    "--icon", (Join-Path $root "assets\icon\wsa-quickdrop.ico"),
    "--distpath", (Join-Path $root "dist"),
    "--workpath", (Join-Path $root "build"),
    "--specpath", $root,
    "--paths", (Join-Path $root "src"),
    (Join-Path $root "quickdrop_entry.py")
)

Write-Host "Release build complete:"
Write-Host (Join-Path $root "dist\WSAQuickDrop.exe")
