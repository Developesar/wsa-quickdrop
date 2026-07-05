from __future__ import annotations

from datetime import datetime

import pytest

from WSAQuickDrop.routes import (
    AndroidPathError,
    append_timestamp_to_name,
    classify_file,
    route_for_file,
    safe_remote_filename,
    validate_android_directory,
)


def test_file_type_routing_defaults() -> None:
    assert route_for_file(r"D:\Samples\image.JPG").remote_path == "/sdcard/Pictures/WSAQuickDrop/image.JPG"
    assert route_for_file(r"D:\Samples\scan.pdf").remote_path == "/sdcard/Download/WSAQuickDrop/scan.pdf"
    assert route_for_file(r"D:\Samples\movie.mp4").remote_path == "/sdcard/Movies/WSAQuickDrop/movie.mp4"
    assert route_for_file(r"D:\Samples\song.flac").remote_path == "/sdcard/Music/WSAQuickDrop/song.flac"
    assert route_for_file(r"D:\Samples\data.bin").remote_path == "/sdcard/Download/WSAQuickDrop/data.bin"


def test_document_extensions_route_to_download_in_auto_mode() -> None:
    assert classify_file("notes.md") == "document"
    assert route_for_file("notes.md").directory == "/sdcard/Download/WSAQuickDrop"


def test_override_modes() -> None:
    assert route_for_file("sample.pdf", mode="pictures").directory == "/sdcard/Pictures/WSAQuickDrop"
    assert route_for_file("sample.jpg", mode="documents").directory == "/sdcard/Documents/WSAQuickDrop"


def test_custom_android_path_validation_accepts_sdcard_child() -> None:
    assert validate_android_directory("/sdcard/My Folder") == "/sdcard/My Folder"
    route = route_for_file("sample.jpg", mode="custom", custom_path="/sdcard/Inbox")
    assert route.remote_path == "/sdcard/Inbox/sample.jpg"


@pytest.mark.parametrize("path", ["", "/system/app", "/data/local", "/", "/sdcard/", "/sdcard/../Download", "/sdcard/bad\npath"])
def test_custom_android_path_validation_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(AndroidPathError):
        validate_android_directory(path)


def test_windows_path_filename_is_preserved() -> None:
    route = route_for_file(r"D:\Samples\my file.pdf")
    assert route.remote_path.endswith("/my file.pdf")


def test_safe_remote_filename_removes_control_characters() -> None:
    assert safe_remote_filename("bad\nname.jpg") == "bad_name.jpg"


def test_timestamp_collision_naming() -> None:
    now = datetime(2026, 7, 5, 12, 30, 1)
    assert append_timestamp_to_name("scan.final.pdf", now=now) == "scan.final-20260705-123001.pdf"
    assert route_for_file("scan.pdf", append_timestamp=True, now=now).remote_path.endswith("scan-20260705-123001.pdf")
