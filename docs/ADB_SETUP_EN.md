# ADB Setup

WSA QuickDrop does not include ADB. Install Android SDK Platform-Tools from the official Android developer site.

## Install Platform-Tools

1. Download Android SDK Platform-Tools for Windows.
2. Extract the zip to a folder such as `C:\Android\platform-tools`.
3. Confirm that `adb.exe` exists in that folder.

## Add ADB to PATH

1. Open Windows search.
2. Search for Environment Variables.
3. Edit your user `Path`.
4. Add the Platform-Tools folder, for example `C:\Android\platform-tools`.
5. Open a new PowerShell window.

Test:

```powershell
adb version
```

## Select ADB manually

If you do not want to change PATH, open WSA QuickDrop and use Browse adb.exe.
In v0.2.0 this is available in Settings.

The selected path is stored locally in:

```text
%APPDATA%\WSAQuickDrop\config.json
```

After ADB is configured, click Connect in WSA QuickDrop. The folder browser should show Pixel 5 folders.
