# Release Guide

## Build and package

```powershell
.\scripts\package_release.ps1
```

This runs tests, builds `dist/WSAQuickDrop.exe`, and creates:

```text
release/WSAQuickDrop-v0.2.0-win-x64/
release/WSAQuickDrop-v0.2.0-win-x64.zip
```

## Release contents

- `WSAQuickDrop.exe`
- `assets/icon/`
- `README.md`
- `README_FA.md`
- `LICENSE`
- `scripts/install_sendto.ps1`
- `scripts/uninstall_sendto.ps1`
- `docs/`

## Manual GitHub release

1. Push the repository to GitHub.
2. Create tag `v0.2.0`.
3. Draft release title: `WSA QuickDrop v0.2.0`.
4. Use the release theme: `Simple Android folder browser for WSA file transfer.`
5. Upload `release/WSAQuickDrop-v0.2.0-win-x64.zip`.
6. Include the 0.2.0 notes from `CHANGELOG.md`.

Do not upload logs, local config files, or test files.
