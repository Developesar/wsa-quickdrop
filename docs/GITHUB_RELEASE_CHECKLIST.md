# GitHub Release Checklist

## Before release

- Run `.\.venv\Scripts\python.exe -m pytest .\src\WSAQuickDrop.Tests`.
- Run `.\scripts\package_release.ps1`.
- Run `.\scripts\check_public_clean.ps1`.
- Smoke-test `release/WSAQuickDrop-v0.2.0-win-x64\WSAQuickDrop.exe --diagnose`.
- Open the GUI and confirm Pixel 5 folder selection is visible.
- Confirm SendTo installer creates `%APPDATA%\Microsoft\Windows\SendTo\WSA QuickDrop.bat`.
- Confirm no personal files, logs, or secrets are staged.
- Replace screenshot mockups with real screenshots if available.
- Confirm personal data scan passes.
- Confirm release zip audit passes.
- Confirm checksum is created.
- Confirm release notes are ready.
- Confirm no release zip is committed unless intentionally changing project policy.
- Confirm no old release artifacts remain.

## GitHub release

- Tag: `v0.2.0`
- Title: `WSA QuickDrop v0.2.0`
- Theme: `Simple Android folder browser for WSA file transfer.`
- Upload: `release/WSAQuickDrop-v0.2.0-win-x64.zip`

## Release notes

Use the 0.2.0 section from `CHANGELOG.md`.
