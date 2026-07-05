from __future__ import annotations

from pathlib import Path

from WSAQuickDrop.transfer import TransferOptions, TransferService


def test_selected_folder_route_sends_all_file_types_to_same_folder() -> None:
    service = TransferService()
    options = TransferOptions(android_folder="/sdcard/Pictures")
    jpg = service._route_for_transfer(Path("image.jpg"), options)
    pdf = service._route_for_transfer(Path("scan.pdf"), options)
    assert jpg.directory == "/sdcard/Pictures"
    assert pdf.directory == "/sdcard/Pictures"
    assert jpg.remote_path == "/sdcard/Pictures/image.jpg"
    assert pdf.remote_path == "/sdcard/Pictures/scan.pdf"


def test_persian_filename_safety_for_selected_folder() -> None:
    service = TransferService()
    route = service._route_for_transfer(Path("گزارش تست.pdf"), TransferOptions(android_folder="/sdcard/Documents"))
    assert route.remote_path == "/sdcard/Documents/گزارش تست.pdf"
