# WSA QuickDrop

![WSA QuickDrop icon](assets/icon/wsa-quickdrop.png)

**Send files from Windows to WSA in one click.**

WSA QuickDrop is a small Windows utility that lets you send files from Windows into Windows Subsystem for Android by choosing an Android folder visually and dropping files.

![WSA QuickDrop main window](assets/screenshots/main-window.png)

The images in this repository are illustrative interface mockups using sample data. Actual application appearance can differ.

## Features

- Visual `Pixel 5` folder browser for WSA storage.
- Friendly folders such as Pictures, Download, Documents, DCIM, Movies, Music, and Ringtones.
- Drag and drop files or use Browse files.
- Explorer `Send to > WSA QuickDrop` integration without admin rights.
- Safe folder creation under the selected Android folder.
- Optional advanced mode for showing internal Android paths.
- ADB discovery, WSA connection diagnostics, media scan request, and local logs.
- CLI still supports smart extension routing with `--target auto`.
- No telemetry, uploads, analytics, or cloud services.

## Quick Start

1. Install Android SDK Platform-Tools so `adb.exe` is available.
2. Enable Developer Mode in Windows Subsystem for Android.
3. Open `WSAQuickDrop.exe`.
4. Click Connect.
5. Choose a folder under Pixel 5, such as Pictures or Download.
6. Drop files into the app.
7. Click Send.
8. In your Android app, open the file picker and browse to Pixel 5 > the selected folder.

## SendTo Setup

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_sendto.ps1
```

Then select files in Explorer and choose:

```text
Right click > Send to > WSA QuickDrop
```

SendTo opens WSA QuickDrop with files queued. It does not send immediately by default, so you can confirm or change the folder first.

## CLI Examples

```powershell
WSAQuickDrop.exe --send "sample.jpg" --folder Pictures
WSAQuickDrop.exe --send "sample.pdf" --folder Download
WSAQuickDrop.exe --send "sample.jpg" --folder "Pictures/My OCR Tests"
WSAQuickDrop.exe --list-folders
WSAQuickDrop.exe --create-folder Pictures "My OCR Tests"
WSAQuickDrop.exe --send "sample.jpg" --target auto
WSAQuickDrop.exe --diagnose
```

## Android OCR App Example

1. Choose Pictures in WSA QuickDrop.
2. Drop an image.
3. Click Send.
4. Open your Android OCR app inside WSA.
5. Choose Select Image.
6. Browse to Pixel 5 > Pictures and select the image.

## Troubleshooting

See [Troubleshooting](docs/TROUBLESHOOTING_EN.md).

Common first checks:

- Run `WSAQuickDrop.exe --diagnose`.
- Confirm WSA Developer Mode is enabled.
- Confirm ADB is installed.
- If a file is not visible immediately, browse directly to Pixel 5 > selected folder.

## Privacy

WSA QuickDrop sends files locally through ADB. It does not upload files, collect analytics, use telemetry, or contact cloud services. Logs stay under `%APPDATA%\WSAQuickDrop\logs`.

See [Security and Privacy](docs/SECURITY_PRIVACY.md).

## Build From Source

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest .\src\WSAQuickDrop.Tests
.\scripts\package_release.ps1
```

The release zip is created at:

```text
release/WSAQuickDrop-v0.2.0-win-x64.zip
```

## License

MIT
