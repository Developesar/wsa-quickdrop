# Troubleshooting

## 1. adb.exe not found

Install Android SDK Platform-Tools, add it to PATH, or choose `adb.exe` in WSA QuickDrop.

## 2. WSA connection refused

Start WSA, enable Developer Mode, open an Android app, and retry `adb connect 127.0.0.1:58526`.

## 3. device offline

Restart WSA, disconnect/reconnect ADB, then run diagnostics again.

## 4. unauthorized

WSA may be waiting for an ADB authorization prompt. Restart WSA and reconnect.

## 5. files pushed but not visible in Images

Check Android file picker paths:

- Pixel 5 > Pictures > WSAQuickDrop
- Pixel 5 > Download > WSAQuickDrop

The Images tab may need a refresh or media scan delay.

## 6. media scanner did not update

The file was still pushed if verification succeeded. Browse by folder instead of using recent media tabs.

## 7. file picker shows no matches

Change the file picker filter from images-only to all files, or browse to the folder manually.

## 8. multiple devices connected

WSA QuickDrop prefers `127.0.0.1:58526` when it is available. Disconnect other devices or use `--connect`.

## 9. WSA not running

Open any Android app installed in WSA, then retry.

## 10. INSTALL/ADB command not recognized

Open a new PowerShell after editing PATH, or select `adb.exe` manually in the app.
