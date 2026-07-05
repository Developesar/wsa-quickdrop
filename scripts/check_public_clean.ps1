param(
    [string]$ReleaseZip = "release\WSAQuickDrop-v0.2.0-win-x64.zip"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$zipPath = Join-Path $root $ReleaseZip
$extractPath = Join-Path $root "release\_verify_extract"

$patterns = @(
    ("Mohamad" + "Milad"),
    ("C:" + '\Users'),
    ("C:" + "/Users"),
    ("Desk" + "top" + '\'),
    ("Desk" + "top" + "/"),
    ("App" + "Data"),
    ("Persian" + "DotsOCR"),
    ("Persian OCR " + "Offline"),
    ("photo_" + "2026")
)

$ignoredDirs = @('\.git\', '\.venv\', '\build\', '\dist\', '\release\', '\.pytest_cache\', '\.pip-cache\', '\__pycache__\')

function Test-IsIgnoredPath {
    param([string]$Path)
    $normalized = $Path.Replace("/", "\")
    foreach ($dir in $ignoredDirs) {
        if ($normalized.Contains($dir)) {
            return $true
        }
    }
    return $false
}

function Search-TextFiles {
    param([string]$BasePath, [string]$Label, [bool]$UseSourceIgnores = $false)
    $hits = @()
    if (-not (Test-Path -LiteralPath $BasePath)) {
        return $hits
    }
    $files = Get-ChildItem -LiteralPath $BasePath -Recurse -File -Force
    foreach ($file in $files) {
        if ($UseSourceIgnores -and (Test-IsIgnoredPath $file.FullName)) {
            continue
        }
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        if ($bytes.Length -gt 2MB) {
            continue
        }
        $text = [System.Text.Encoding]::UTF8.GetString($bytes)
        foreach ($pattern in $patterns) {
            if ($text.Contains($pattern)) {
                $hits += [pscustomobject]@{ Area = $Label; File = $file.FullName.Substring($BasePath.Length).TrimStart("\", "/"); Pattern = $pattern }
            }
        }
    }
    return $hits
}

function Search-Bytes {
    param([string]$BasePath, [string]$Label, [bool]$UseSourceIgnores = $false)
    $hits = @()
    if (-not (Test-Path -LiteralPath $BasePath)) {
        return $hits
    }
    $files = Get-ChildItem -LiteralPath $BasePath -Recurse -File -Force
    foreach ($file in $files) {
        if ($UseSourceIgnores -and (Test-IsIgnoredPath $file.FullName)) {
            continue
        }
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $latin = [System.Text.Encoding]::ASCII.GetString($bytes)
        foreach ($pattern in $patterns) {
            if ($latin.Contains($pattern)) {
                $hits += [pscustomobject]@{ Area = $Label; File = $file.FullName.Substring($BasePath.Length).TrimStart("\", "/"); Pattern = $pattern }
            }
        }
    }
    return $hits
}

if (Test-Path -LiteralPath $extractPath) {
    Remove-Item -LiteralPath $extractPath -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $extractPath | Out-Null
if (Test-Path -LiteralPath $zipPath) {
    Expand-Archive -LiteralPath $zipPath -DestinationPath $extractPath -Force
}

$hits = @()
$hits += Search-TextFiles -BasePath $root -Label "source" -UseSourceIgnores $true
$releaseFolder = Join-Path $root "release\WSAQuickDrop-v0.2.0-win-x64"
$hits += Search-TextFiles -BasePath $releaseFolder -Label "release-folder"
$hits += Search-TextFiles -BasePath $extractPath -Label "extracted-zip"
$hits += Search-Bytes -BasePath $extractPath -Label "extracted-zip-bytes"

$blockedNames = @("__pycache__", ".venv", "config.json")
$blockedHits = @()
foreach ($name in $blockedNames) {
    $blockedHits += Get-ChildItem -LiteralPath $extractPath -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq $name }
}

if (Test-Path -LiteralPath $extractPath) {
    Remove-Item -LiteralPath $extractPath -Recurse -Force
}

if ($hits.Count -gt 0 -or $blockedHits.Count -gt 0) {
    Write-Host "Public clean check: FAIL"
    if ($hits.Count -gt 0) {
        $hits | Format-Table -AutoSize
    }
    if ($blockedHits.Count -gt 0) {
        Write-Host "Blocked files found in extracted zip:"
        $blockedHits | Select-Object FullName | Format-Table -AutoSize
    }
    exit 1
}

Write-Host "Public clean check: PASS"
