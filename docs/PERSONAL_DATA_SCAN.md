# Personal Data Scan

## Scope

The source tree, release folder, and extracted release zip were scanned for local-machine and private-project traces.

## Search Terms Used

The scan used the same private-reference patterns implemented in `scripts/check_public_clean.ps1`, covering:

- the local Windows account name
- Windows user-root absolute paths
- slash and backslash forms of local user paths
- local workspace folder markers
- local application-data folder markers
- private OCR project identifiers
- private photo filename patterns

The script composes those patterns from fragments so the scanner does not flag its own implementation.

## Files Changed

- README files now describe a generic Android OCR app example.
- User guides now describe generic Android app file-picker usage.
- Unused OCR-specific GUI helper text was removed.
- Tests now use generic sample drive paths instead of user-profile paths.
- A duplicate Android SDK discovery path with a local application-data marker was removed.

## Result

`scripts/check_public_clean.ps1` reported `PASS`.

## Remaining Allowed Terms

No personal local paths or private-project names remain in public docs or packaged release content. Generic environment variables and runtime diagnostics may still show a user's own local paths when the app is executed on that user's machine.
