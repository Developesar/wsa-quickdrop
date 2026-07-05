# Release Zip Audit

## Artifact

- Zip: `release/WSAQuickDrop-v0.2.0-win-x64.zip`
- Size: `10128919` bytes
- SHA256: `5d0c2aae3f26bce452073c1ce887e8e58b38a7f6566d77461cb37671715f140d`

## Included Top-Level Files

- `assets/`
- `docs/`
- `scripts/`
- `CHANGELOG.md`
- `LICENSE`
- `README.md`
- `README_FA.md`
- `WSAQuickDrop.exe`

## Excluded From Binary Zip

The following source-only release process files are intentionally not included in the binary zip:

- `docs/RELEASE_NOTES_v0.2.0.md`
- `docs/RELEASE_ZIP_AUDIT.md`
- `docs/PUBLIC_RELEASE_CLEANUP_REPORT.md`
- `docs/PERSONAL_DATA_SCAN.md`
- `docs/PUBLISH_COMMANDS.md`

This avoids a self-referential checksum file inside the zip and keeps the user-facing package focused.

## Scan Result

- Source scan: pass
- Release folder scan: pass
- Extracted zip text scan: pass
- Extracted zip byte scan: pass
- Blocked generated files check: pass

## Old Version Artifact Check

Only v0.2.0 release artifacts remain under `release/`:

- `WSAQuickDrop-v0.2.0-win-x64/`
- `WSAQuickDrop-v0.2.0-win-x64.zip`
- `WSAQuickDrop-v0.2.0-win-x64.zip.sha256`

## Final Status

Release zip audit passed.
