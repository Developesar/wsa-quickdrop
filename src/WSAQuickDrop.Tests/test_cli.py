from __future__ import annotations

from WSAQuickDrop.cli import build_parser, collect_send_files, options_from_args
from WSAQuickDrop.config import AppConfig


def test_cli_folder_parsing_maps_pictures() -> None:
    args = build_parser().parse_args(["--send", "sample.jpg", "--folder", "Pictures"])
    options = options_from_args(args, AppConfig())
    assert options.android_folder == "/sdcard/Pictures"
    assert collect_send_files(args) == ["sample.jpg"]


def test_cli_positional_files_are_for_gui_sendto_mode() -> None:
    args = build_parser().parse_args(["sample.jpg", "sample.pdf"])
    assert collect_send_files(args) == []


def test_cli_nested_folder_parsing() -> None:
    args = build_parser().parse_args(["--send", "sample.jpg", "--folder", "Pictures/My OCR Tests"])
    options = options_from_args(args, AppConfig())
    assert options.android_folder == "/sdcard/Pictures/My OCR Tests"
