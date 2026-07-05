from __future__ import annotations

import os
import sys
from pathlib import Path


SENDTO_NAME = "WSA QuickDrop.bat"
CONTEXT_MENU_KEY = r"Software\Classes\*\shell\WSAQuickDrop"


def sendto_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set.")
    return Path(appdata) / "Microsoft" / "Windows" / "SendTo"


def sendto_batch_path() -> Path:
    return sendto_dir() / SENDTO_NAME


def source_launcher() -> Path:
    return Path(__file__).resolve().parents[2] / "quickdrop_entry.py"


def resolve_executable_for_launcher(exe_path: str | None = None) -> tuple[str, list[str]]:
    if exe_path:
        return str(Path(exe_path).resolve()), []
    if getattr(sys, "frozen", False):
        return sys.executable, []
    launcher = source_launcher()
    return sys.executable, [str(launcher)]


def build_sendto_batch(executable: str, prefix_args: list[str] | None = None) -> str:
    args = " ".join(f'"{arg}"' for arg in (prefix_args or []))
    spacer = " " if args else ""
    return "\r\n".join(
        [
            "@echo off",
            "setlocal",
            f'"{executable}" {args}{spacer}%*',
            "exit /b %ERRORLEVEL%",
            "",
        ]
    )


def install_sendto(exe_path: str | None = None) -> Path:
    target_dir = sendto_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    executable, prefix_args = resolve_executable_for_launcher(exe_path)
    batch = sendto_batch_path()
    batch.write_text(build_sendto_batch(executable, prefix_args), encoding="utf-8")
    return batch


def uninstall_sendto() -> bool:
    removed = False
    for path in [sendto_batch_path(), sendto_dir() / "WSA QuickDrop.lnk"]:
        if path.exists():
            path.unlink()
            removed = True
    return removed


def build_context_menu_command(exe_path: str | None = None) -> str:
    executable, prefix_args = resolve_executable_for_launcher(exe_path)
    quoted = [f'"{executable}"', *[f'"{arg}"' for arg in prefix_args], '"%1"']
    return " ".join(quoted)


def install_context_menu(exe_path: str | None = None) -> None:
    if os.name != "nt":
        raise RuntimeError("Windows context menu registration is only available on Windows.")
    import winreg

    command = build_context_menu_command(exe_path)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_KEY) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Send to WSA QuickDrop")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, command.split('"')[1])
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_KEY + r"\command") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)


def uninstall_context_menu() -> None:
    if os.name != "nt":
        raise RuntimeError("Windows context menu registration is only available on Windows.")
    import winreg

    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_KEY + r"\command")
    except FileNotFoundError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_KEY)
    except FileNotFoundError:
        pass
