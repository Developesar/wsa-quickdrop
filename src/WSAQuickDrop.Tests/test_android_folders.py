from __future__ import annotations

import pytest

from WSAQuickDrop.android_folders import (
    AndroidFolder,
    build_child_folder_path,
    friendly_from_android_path,
    friendly_to_android_path,
    merge_builtin_and_discovered,
    parse_ls_directories,
    selected_folder_from_config,
    validate_folder_name,
)
from WSAQuickDrop.routes import AndroidPathError


def test_friendly_folder_mapping() -> None:
    assert friendly_to_android_path("Pictures") == "/sdcard/Pictures"
    assert friendly_to_android_path("Download") == "/sdcard/Download"
    assert friendly_to_android_path("downloads") == "/sdcard/Download"
    assert friendly_to_android_path("Pictures/My OCR Tests") == "/sdcard/Pictures/My OCR Tests"
    assert friendly_from_android_path("/sdcard/Pictures/My OCR Tests") == "Pictures/My OCR Tests"


def test_selected_pictures_maps_without_quickdrop_subfolder() -> None:
    selected = selected_folder_from_config("/sdcard/Pictures", "Pictures", "")
    assert selected == AndroidFolder("Pictures", "/sdcard/Pictures")


def test_list_folder_parser_and_merge() -> None:
    output = "Pictures/\nDownload/\nMy OCR Tests/\n/sdcard/Pictures/My OCR Tests\nbad/name/\n"
    discovered = parse_ls_directories(output)
    assert "Pictures" in discovered
    assert "My OCR Tests" in discovered
    assert "Pictures/My OCR Tests" in discovered
    folders = merge_builtin_and_discovered(discovered)
    paths = [folder.android_path for folder in folders]
    assert "/sdcard/Pictures" in paths
    assert "/sdcard/DCIM" in paths
    assert "/sdcard/My OCR Tests" in paths
    assert "/sdcard/Pictures/My OCR Tests" in paths


@pytest.mark.parametrize("name", ["", "bad/name", "bad\\name", "..", "two..dots", "bad\nname", "trail "])
def test_create_folder_validation_rejects_unsafe_names(name: str) -> None:
    with pytest.raises(ValueError):
        validate_folder_name(name)


def test_build_child_folder_path_handles_spaces_and_persian() -> None:
    friendly, android = build_child_folder_path("/sdcard/Pictures", "تست OCR")
    assert friendly == "Pictures/تست OCR"
    assert android == "/sdcard/Pictures/تست OCR"


def test_empty_destination_is_rejected() -> None:
    with pytest.raises(AndroidPathError):
        friendly_to_android_path("")
