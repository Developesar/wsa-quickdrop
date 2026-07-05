# UI Redesign

Version 0.2.0 changes WSA QuickDrop from an ADB/path-oriented utility into a folder-first Windows app.

## Main model

The user answers one question:

```text
Where do you want to put this file inside WSA?
```

The answer is selected visually under:

```text
Pixel 5
  Pictures
  Download
  Documents
  DCIM
  Movies
  Music
  Ringtones
```

## Normal mode

Normal mode hides paths like `/sdcard/Pictures`. Users choose friendly folder names and send files.

## Advanced mode

Settings includes Show advanced Android path. When enabled, the selected internal path appears below the folder browser.

## SendTo behavior

SendTo opens the app with files queued. Immediate send is off by default so files do not go to an unexpected folder.

## CLI compatibility

The CLI supports the new folder mode:

```powershell
WSAQuickDrop.exe --send "sample.jpg" --folder Pictures
```

Old target routing remains available:

```powershell
WSAQuickDrop.exe --send "sample.jpg" --target auto
```
