# WSA QuickDrop v0.2.0

## Summary

A simple Windows utility for sending files into Windows Subsystem for Android by choosing an Android folder visually.

## Highlights

- Visual Pixel 5 folder browser
- Drag and drop file queue
- Explorer SendTo integration
- CLI support
- `--folder`, `--list-folders`, and `--create-folder`
- Fixed empty destination `mkdir` bug
- No telemetry, no uploads, no cloud services

## Installation

1. Download `WSAQuickDrop-v0.2.0-win-x64.zip`.
2. Extract it.
3. Run `WSAQuickDrop.exe`.
4. Optional: run `scripts/install_sendto.ps1`.

## Requirements

- Windows
- Windows Subsystem for Android
- WSA Developer Mode enabled
- Android SDK Platform-Tools / `adb.exe`

## Known Limitations

- WSA must be running.
- ADB must be installed.
- Android media indexing may take a moment after files are sent.
- Microsoft has discontinued official WSA distribution, but existing installations may still work.

## Checksum

SHA256: `5d0c2aae3f26bce452073c1ce887e8e58b38a7f6566d77461cb37671715f140d`

