# Technical Decision

## Chosen stack

Python 3.11 with Tkinter GUI and PyInstaller packaging.

## Why

The requested first choice was C# with .NET 8. On this machine, `dotnet.exe` exists, but `dotnet --info` reported no installed SDKs. Only .NET 6 runtimes were present, so a .NET 8 WinForms or WPF project could not be created or built locally.

Python 3.11.9 and Tkinter are available locally, and PyInstaller 6.11.1 is also available. That matches the requested fallback path:

- Python 3.11+
- Tkinter GUI
- optional PyInstaller packaging

## Tradeoffs

- Native Explorer integration is still handled through user-level scripts and requires no admin rights.
- Tkinter keeps dependencies small and avoids requiring a Python GUI framework.
- The release build uses PyInstaller to create `WSAQuickDrop.exe`.
- Plain Tkinter does not provide Explorer drag-and-drop by default, so the app includes a small Windows `WM_DROPFILES` hook implemented with `ctypes`.

## Build outputs

The packaging scripts produce:

- Source/dev run: `python quickdrop_entry.py`
- Portable executable: `dist/WSAQuickDrop.exe`
- Release zip: `release/WSAQuickDrop-v0.2.0-win-x64.zip`

## v0.2.0 UI direction

The GUI now uses a visual Pixel 5 folder browser. Internal Android paths are hidden unless the user enables advanced mode in Settings. The CLI keeps the older extension routing options for compatibility.
