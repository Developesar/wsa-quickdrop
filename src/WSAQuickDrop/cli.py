from __future__ import annotations

import argparse
import os
import platform
import sys
from pathlib import Path

from . import APP_NAME, APP_VERSION, DEFAULT_WSA_HOST, DEFAULT_WSA_PORT
from .adb import AdbClient, AdbDiscovery
from .config import AppConfig, parse_endpoint
from .sendto import (
    install_context_menu,
    install_sendto,
    sendto_batch_path,
    uninstall_context_menu,
    uninstall_sendto,
)
from .transfer import TransferOptions, TransferService


PERSIAN_OCR_PACKAGES = ["ir.persiandots.ocr.dev", "ir.persiandots.ocr"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wsa-quickdrop",
        description="Send files from Windows to Windows Subsystem for Android storage using ADB.",
    )
    parser.add_argument("files", nargs="*", help="Files to send. If omitted, the GUI opens.")
    parser.add_argument("--send", dest="send_files", nargs="*", help="Send one or more files without opening the GUI.")
    parser.add_argument("--target", default=None, choices=["auto", "pictures", "downloads", "documents", "movies", "music", "custom"])
    parser.add_argument("--custom-path", default=None, help="Custom Android destination path below /sdcard/.")
    parser.add_argument("--connect", default=None, help="WSA ADB endpoint, for example 127.0.0.1:58526.")
    parser.add_argument("--adb", default=None, help="Path to adb.exe.")
    parser.add_argument("--scan", dest="scan", action="store_true", default=None, help="Trigger Android media scanner after push.")
    parser.add_argument("--no-scan", dest="scan", action="store_false", help="Skip Android media scanner.")
    parser.add_argument("--append-timestamp", action="store_true", help="Append a timestamp to pushed filenames.")
    parser.add_argument("--install-sendto", action="store_true", help="Install the Explorer SendTo shortcut.")
    parser.add_argument("--uninstall-sendto", action="store_true", help="Remove the Explorer SendTo shortcut.")
    parser.add_argument("--install-context-menu", action="store_true", help="Install optional HKCU classic context-menu item.")
    parser.add_argument("--uninstall-context-menu", action="store_true", help="Remove optional HKCU classic context-menu item.")
    parser.add_argument("--list-devices", action="store_true", help="Print adb devices.")
    parser.add_argument("--diagnose", action="store_true", help="Print diagnostics and troubleshooting hints.")
    parser.add_argument("--verbose", action="store_true", help="Print extra transfer details.")
    parser.add_argument("--version", action="store_true", help="Print app version.")
    return parser


def options_from_args(args: argparse.Namespace, config: AppConfig) -> TransferOptions:
    host, port = parse_endpoint(args.connect, config.wsaHost, config.wsaPort)
    return TransferOptions(
        target=args.target or config.defaultRouteMode,
        custom_path=args.custom_path or config.lastDestination,
        adb_path=args.adb or config.adbPath,
        host=host,
        port=port,
        scan=config.autoMediaScan if args.scan is None else args.scan,
        append_timestamp=args.append_timestamp or config.appendTimestampOnCollision,
        verbose=args.verbose,
    )


def collect_send_files(args: argparse.Namespace) -> list[str]:
    if args.send_files is not None:
        return args.send_files
    return args.files or []


def print_devices(config: AppConfig, override_adb: str = "") -> int:
    discovery = AdbDiscovery()
    adb_path = discovery.find_adb(override_adb or config.adbPath)
    if adb_path is None:
        print("adb.exe not found.")
        return 2
    client = AdbClient(adb_path)
    devices, result = client.devices()
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if not devices:
        print("No devices detected.")
    return 0 if result.ok else result.returncode


def diagnose(config: AppConfig, args: argparse.Namespace) -> int:
    discovery = AdbDiscovery()
    options = options_from_args(args, config)
    adb_path = discovery.find_adb(options.adb_path)
    print(f"{APP_NAME} {APP_VERSION}")
    print(f"OS: {platform.platform()}")
    print(f"Python: {platform.python_version()} ({sys.executable})")
    print(f"Config path: {AppConfig.config_path()}")
    print(f"WSA endpoint: {options.host}:{options.port}")
    print(f"SendTo installed: {'yes' if sendto_batch_path().exists() else 'no'}")
    print(f"ADB detected: {adb_path if adb_path else 'no'}")
    if adb_path is None:
        print("Suggestion: install Android SDK Platform-Tools or choose adb.exe in the GUI.")
        return 2
    client = AdbClient(adb_path)
    version = client.version()
    print("ADB version:")
    print(version.stdout or version.stderr or "(no output)")
    devices, result = client.devices()
    print("ADB devices:")
    print(result.stdout or result.stderr or "(no output)")
    preferred = f"{options.host}:{options.port}"
    chosen = client.choose_device(devices, preferred)
    if chosen is None:
        print("WSA connection: not ready")
        print("Suggestion: open WSA Settings, enable Developer Mode, start an Android app, then retry.")
    elif chosen.state == "device":
        print(f"WSA connection: ready ({chosen.serial})")
    else:
        print(f"WSA connection: {chosen.serial} is {chosen.state}")
    return 0


def run_send(files: list[str], config: AppConfig, args: argparse.Namespace) -> int:
    if not files:
        print("No files were provided for --send.", file=sys.stderr)
        return 2
    service = TransferService(config=config)
    options = options_from_args(args, config)
    summary = service.send_files(files, options)
    for message in summary.messages:
        print(message)
    for item in summary.items:
        destination = item.remote_path or item.remote_dir or "(not routed)"
        print(f"{item.status.upper()}: {item.local_path} -> {destination}")
        if item.message:
            print(f"  {item.message}")
    return 0 if summary.ok else 1


def launch_gui(config: AppConfig) -> int:
    from .gui import run_gui

    run_gui(config)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = AppConfig.load()

    if args.version:
        print(f"{APP_NAME} {APP_VERSION}")
        return 0
    if args.install_sendto:
        path = install_sendto()
        print(f"Installed SendTo launcher: {path}")
        return 0
    if args.uninstall_sendto:
        removed = uninstall_sendto()
        print("Removed SendTo launcher." if removed else "SendTo launcher was not installed.")
        return 0
    if args.install_context_menu:
        install_context_menu()
        print("Installed optional HKCU context-menu item.")
        return 0
    if args.uninstall_context_menu:
        uninstall_context_menu()
        print("Removed optional HKCU context-menu item.")
        return 0
    if args.list_devices:
        return print_devices(config, args.adb or "")
    if args.diagnose:
        return diagnose(config, args)

    files = collect_send_files(args)
    if files:
        return run_send(files, config, args)
    return launch_gui(config)
