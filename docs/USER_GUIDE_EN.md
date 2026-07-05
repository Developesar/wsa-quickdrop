# User Guide

## Simple Flow

1. Open WSA QuickDrop.
2. Click Connect.
3. Choose an Android folder from Pixel 5, such as Pictures, Download, Documents, or DCIM.
4. Drop files into the app or use Browse files.
5. Click Send.
6. Open your Android app and browse to Pixel 5 > the selected folder.

The main GUI sends every queued file to the selected folder. It does not switch destinations by extension.

## SendTo Flow

1. Install the SendTo shortcut.
2. Select files in Windows Explorer.
3. Right click > Send to > WSA QuickDrop.
4. WSA QuickDrop opens with files queued.
5. Confirm the folder, then click Send.

Immediate send from SendTo is available in Settings but is off by default.

## Folder Browser

The left panel shows Pixel 5. This is the friendly name for WSA Android storage. Normal mode hides internal paths such as `/sdcard`.

Advanced users can enable Show advanced Android path in Settings.

## Create Folder

1. Select a parent folder, such as Pictures.
2. Click Create folder.
3. Enter a safe folder name, for example My OCR Tests.
4. The app creates Pixel 5 > Pictures > My OCR Tests and selects it.

## CLI

```powershell
WSAQuickDrop.exe --send "sample.jpg" --folder Pictures
WSAQuickDrop.exe --send "sample.pdf" --folder Download
WSAQuickDrop.exe --send "sample.jpg" --folder "Pictures/My OCR Tests"
WSAQuickDrop.exe --list-folders
WSAQuickDrop.exe --create-folder Pictures "My OCR Tests"
```

Smart extension routing is still available:

```powershell
WSAQuickDrop.exe --send "sample.jpg" --target auto
```

## Persian OCR Offline Example

1. Choose Pictures.
2. Drop an image.
3. Click Send.
4. Open Persian OCR Offline.
5. Choose Select Image.
6. Browse to Pixel 5 > Pictures.
7. Select the image.
