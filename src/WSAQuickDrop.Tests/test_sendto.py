from __future__ import annotations

from WSAQuickDrop.sendto import build_context_menu_command, build_sendto_batch


def test_sendto_batch_passes_all_selected_files() -> None:
    batch = build_sendto_batch(r"C:\Tools\WSAQuickDrop.exe")
    assert r'"C:\Tools\WSAQuickDrop.exe" %*' in batch
    assert "--send" not in batch


def test_sendto_batch_supports_source_launcher_prefix() -> None:
    batch = build_sendto_batch(r"C:\Python311\python.exe", [r"C:\Repo\quickdrop_entry.py"])
    assert r'"C:\Python311\python.exe" "C:\Repo\quickdrop_entry.py" %*' in batch


def test_context_menu_command_uses_single_selected_file(monkeypatch) -> None:
    monkeypatch.setattr("WSAQuickDrop.sendto.resolve_executable_for_launcher", lambda _=None: (r"C:\Tools\WSAQuickDrop.exe", []))
    command = build_context_menu_command()
    assert command == r'"C:\Tools\WSAQuickDrop.exe" "%1"'
