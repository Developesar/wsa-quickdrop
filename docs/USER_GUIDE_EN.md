# User Guide

## Right-click flow

1. Run `scripts/install_sendto.ps1`.
2. Select one or more files in Windows Explorer.
3. Right click the selection.
4. Choose `Send to > WSA QuickDrop`.
5. The app sends files to WSA through ADB.

## Drag-drop flow

1. Open `WSAQuickDrop.exe`.
2. Drop files into the window or use Browse Files.
3. Choose a destination mode.
4. Click Send to WSA.

## Destination modes

- Auto: routes by file type.
- Pictures: sends everything to `/sdcard/Pictures/WSAQuickDrop`.
- Downloads: sends everything to `/sdcard/Download/WSAQuickDrop`.
- Documents: sends everything to `/sdcard/Documents/WSAQuickDrop`.
- Movies: sends everything to `/sdcard/Movies/WSAQuickDrop`.
- Music: sends everything to `/sdcard/Music/WSAQuickDrop`.
- Custom: sends to a user path below `/sdcard/`.

## CLI flow

```powershell
WSAQuickDrop.exe --send "C:\Users\User\Desktop\sample.jpg"
WSAQuickDrop.exe --send "sample.pdf" --target downloads
WSAQuickDrop.exe --send "sample.jpg" --target custom --custom-path "/sdcard/Pictures/MyInbox"
WSAQuickDrop.exe --diagnose
```

## Persian OCR Offline example

1. Send images or PDFs with WSA QuickDrop.
2. Open Persian OCR Offline inside WSA.
3. Choose Select Image/PDF.
4. In Android file picker, choose Pixel 5.
5. Open Pictures or Download.
6. Open WSAQuickDrop.

The helper can check these optional packages:

- `ir.persiandots.ocr.dev`
- `ir.persiandots.ocr`
