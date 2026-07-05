$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
& (Join-Path $PSScriptRoot "build_release.ps1")

$version = "0.1.0"
$releaseRoot = Join-Path $root "release"
$packageDir = Join-Path $releaseRoot "WSAQuickDrop-v$version-win-x64"
$zipPath = Join-Path $releaseRoot "WSAQuickDrop-v$version-win-x64.zip"

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -LiteralPath $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null

Copy-Item -LiteralPath (Join-Path $root "dist\WSAQuickDrop.exe") -Destination (Join-Path $packageDir "WSAQuickDrop.exe") -Force
Copy-Item -LiteralPath (Join-Path $root "README.md") -Destination $packageDir -Force
Copy-Item -LiteralPath (Join-Path $root "README_FA.md") -Destination $packageDir -Force
Copy-Item -LiteralPath (Join-Path $root "LICENSE") -Destination $packageDir -Force
Copy-Item -LiteralPath (Join-Path $root "CHANGELOG.md") -Destination $packageDir -Force
Copy-Item -LiteralPath (Join-Path $root "docs") -Destination $packageDir -Recurse -Force
Copy-Item -LiteralPath (Join-Path $root "assets") -Destination $packageDir -Recurse -Force
$releaseScripts = Join-Path $packageDir "scripts"
New-Item -ItemType Directory -Force -Path $releaseScripts | Out-Null
Copy-Item -LiteralPath (Join-Path $root "scripts\install_sendto.ps1") -Destination $releaseScripts -Force
Copy-Item -LiteralPath (Join-Path $root "scripts\uninstall_sendto.ps1") -Destination $releaseScripts -Force
Copy-Item -LiteralPath (Join-Path $root "scripts\install_context_menu.ps1") -Destination $releaseScripts -Force
Copy-Item -LiteralPath (Join-Path $root "scripts\uninstall_context_menu.ps1") -Destination $releaseScripts -Force

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -LiteralPath $packageDir -DestinationPath $zipPath -Force

Write-Host "Release package complete:"
Write-Host $zipPath
