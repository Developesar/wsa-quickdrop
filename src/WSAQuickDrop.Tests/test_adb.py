from __future__ import annotations

import pytest

from WSAQuickDrop.adb import AdbCommandFactory, AdbDevice, AdbDiscovery, parse_adb_devices, shell_quote
from WSAQuickDrop.routes import AndroidPathError


def test_parse_adb_devices() -> None:
    output = """List of devices attached
127.0.0.1:58526	device
emulator-5554	offline
"""
    devices = parse_adb_devices(output)
    assert devices[0] == AdbDevice("127.0.0.1:58526", "device", "")
    assert devices[1].state == "offline"


def test_adb_command_building_uses_argument_lists() -> None:
    assert AdbCommandFactory.push_args(r"C:\tmp\a b.jpg", "/sdcard/Pictures/WSAQuickDrop/a b.jpg") == [
        "push",
        r"C:\tmp\a b.jpg",
        "/sdcard/Pictures/WSAQuickDrop/a b.jpg",
    ]
    mkdir = AdbCommandFactory.mkdir_args("/sdcard/Pictures/WSAQuickDrop")
    assert mkdir[0] == "shell"
    assert mkdir[1] == "mkdir -p '/sdcard/Pictures/WSAQuickDrop'"


def test_mkdir_empty_argument_regression() -> None:
    with pytest.raises(AndroidPathError):
        AdbCommandFactory.mkdir_args("")


def test_mkdir_folder_with_spaces_is_quoted() -> None:
    args = AdbCommandFactory.mkdir_args("/sdcard/Pictures/My OCR Tests")
    assert args == ["shell", "mkdir -p '/sdcard/Pictures/My OCR Tests'"]


def test_media_scan_command_generation() -> None:
    args = AdbCommandFactory.media_scan_args("/sdcard/Pictures/WSAQuickDrop/sample.jpg")
    assert args[0] == "shell"
    assert "MEDIA_SCANNER_SCAN_FILE" in args[1]
    assert "file:///sdcard/Pictures/WSAQuickDrop/sample.jpg" in args[1]


def test_shell_quote_handles_single_quotes() -> None:
    assert shell_quote("/sdcard/O'Brien/file.jpg") == "'/sdcard/O'\"'\"'Brien/file.jpg'"


def test_adb_discovery_prefers_custom_path(tmp_path) -> None:
    adb = tmp_path / "adb.exe"
    adb.write_text("", encoding="utf-8")
    discovery = AdbDiscovery(env={})
    assert discovery.find_adb(str(adb)) == adb
