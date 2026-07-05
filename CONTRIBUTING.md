# Contributing

Thanks for helping improve WSA QuickDrop.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest .\src\WSAQuickDrop.Tests
```

## Guidelines

- Keep normal usage admin-free.
- Do not bundle `adb.exe` or Android Platform-Tools.
- Do not add telemetry, analytics, uploads, or cloud services.
- Keep Android custom paths restricted to `/sdcard/`.
- Prefer small, testable changes in the core package.

## Release Checks

Before opening a release PR, run:

```powershell
.\scripts\package_release.ps1
```
