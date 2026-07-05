# Public Release Cleanup Report

## Release

- Product: WSA QuickDrop
- Version: `0.2.0`
- Branch: `release/v0.2.0-public-cleanup`

## Cleanup Summary

- Removed old v0.1.0 generated release folder and zip.
- Removed generated build output and cache folders before final packaging.
- Removed generated PyInstaller spec file containing local build paths.
- Removed OCR-specific public text so the project reads as a generic WSA utility.
- Rebuilt the v0.2.0 binary release package.
- Created SHA256 checksum for the final zip.
- Created release notes and manual publish commands.

## Validation

- Unit tests: `44 passed`
- Package build: passed
- Public clean scan: passed
- Release zip audit: passed
- Packaged `--help`: passed
- Packaged `--diagnose`: passed
- Packaged `--list-folders`: passed
- Live WSA send test: passed with generated public sample text file

## Release Outputs

- `release/WSAQuickDrop-v0.2.0-win-x64/`
- `release/WSAQuickDrop-v0.2.0-win-x64.zip`
- `release/WSAQuickDrop-v0.2.0-win-x64.zip.sha256`

## Notes

Release artifacts are intentionally ignored by Git and should be uploaded to a GitHub Release rather than committed.
