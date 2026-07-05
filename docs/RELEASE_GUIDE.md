# Release Guide

## Build

```powershell
.\scripts\build_release.ps1
```

This restores dev dependencies into `.venv`, runs tests, compiles Python files, and creates:

```text
dist/WSAQuickDrop.exe
```

## Package

```powershell
.\scripts\package_release.ps1
```

This creates:

```text
release/WSAQuickDrop-v0.1.0-win-x64/
release/WSAQuickDrop-v0.1.0-win-x64.zip
```

## Manual GitHub release

1. Push the repo to GitHub.
2. Create a tag, for example `v0.1.0`.
3. Draft a new GitHub Release.
4. Upload `release/WSAQuickDrop-v0.1.0-win-x64.zip`.
5. Include notes from `CHANGELOG.md`.

Do not upload secrets or local config/log files.
