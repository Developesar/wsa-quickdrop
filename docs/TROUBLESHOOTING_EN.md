# Troubleshooting

## Run diagnostics

```powershell
WSAQuickDrop.exe --diagnose
```

## adb.exe not found

Install Android SDK Platform-Tools, add it to PATH, or choose `adb.exe` in Settings.

## WSA not connected

Open Windows Subsystem for Android settings, enable Developer Mode, start an Android app, then click Connect.

## Multiple devices

WSA QuickDrop prefers `127.0.0.1:58526` when available. Disconnect other ADB devices or pass `--connect`.

## Folder browser empty

WSA may not be running, Developer Mode may be disabled, or ADB may not be connected. Click Connect, then Refresh folders.

## mkdir: Needs 1 argument

This was an older empty-destination bug. Version 0.2.0 validates the destination before building `adb shell mkdir -p`. If you still see this, run `--diagnose` and make sure a Pixel 5 folder is selected.

## Permission denied

Choose a normal Pixel 5 folder such as Pictures or Download. Custom Android paths outside `/sdcard/` are blocked.

## Files pushed but not visible in Images

Browse directly to Pixel 5 > selected folder. Media tabs may refresh later even when the file is already present.

## File picker shows no matches

Change the file picker filter to all files, or browse to the folder manually.

## Persian filenames

Persian filenames and folder names are preserved where ADB and the Android file picker support Unicode. If a target app does not show them, browse by folder rather than recent files.
