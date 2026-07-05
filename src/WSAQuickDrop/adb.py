from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from . import DEFAULT_WSA_HOST, DEFAULT_WSA_PORT
from .process_runner import CommandResult, ProcessRunner
from .routes import validate_android_directory


@dataclass(frozen=True)
class AdbDevice:
    serial: str
    state: str
    details: str = ""


class AdbDiscovery:
    def __init__(self, env: dict[str, str] | None = None) -> None:
        self.env = env or os.environ

    def candidate_paths(self, custom_path: str | None = None) -> list[Path]:
        candidates: list[Path] = []
        if custom_path:
            candidates.append(Path(os.path.expandvars(custom_path)).expanduser())
        which = shutil.which("adb")
        if which:
            candidates.append(Path(which))
        local_appdata = self.env.get("LOCALAPPDATA")
        user_profile = self.env.get("USERPROFILE")
        if local_appdata:
            candidates.append(Path(local_appdata) / "Android" / "Sdk" / "platform-tools" / "adb.exe")
        for env_name in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
            sdk = self.env.get(env_name)
            if sdk:
                candidates.append(Path(sdk) / "platform-tools" / "adb.exe")
        if user_profile:
            candidates.extend(
                [
                    Path(user_profile) / "Android" / "Sdk" / "platform-tools" / "adb.exe",
                ]
            )
        for program_var in ("ProgramFiles", "ProgramFiles(x86)"):
            program_dir = self.env.get(program_var)
            if program_dir:
                candidates.append(Path(program_dir) / "Android" / "Android Studio" / "jbr" / "bin" / "adb.exe")
        unique: list[Path] = []
        seen: set[str] = set()
        for candidate in candidates:
            key = str(candidate).lower()
            if key not in seen:
                unique.append(candidate)
                seen.add(key)
        return unique

    @staticmethod
    def is_adb_path(path: Path) -> bool:
        return path.is_file() and path.name.lower() == "adb.exe"

    def find_adb(self, custom_path: str | None = None) -> Path | None:
        for candidate in self.candidate_paths(custom_path):
            if self.is_adb_path(candidate):
                return candidate
        return None


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


class AdbCommandFactory:
    @staticmethod
    def mkdir_args(remote_dir: str) -> list[str]:
        directory = validate_android_directory(remote_dir)
        return ["shell", f"mkdir -p {shell_quote(directory)}"]

    @staticmethod
    def list_sdcard_dirs_args() -> list[str]:
        return ["shell", "find /sdcard -mindepth 1 -maxdepth 2 -type d 2>/dev/null || ls -1 -p /sdcard"]

    @staticmethod
    def push_args(local_path: str | Path, remote_path: str) -> list[str]:
        return ["push", str(local_path), remote_path]

    @staticmethod
    def ls_args(remote_path: str) -> list[str]:
        return ["shell", f"ls -l {shell_quote(remote_path)}"]

    @staticmethod
    def media_scan_args(remote_path: str) -> list[str]:
        uri = f"file://{remote_path}"
        return [
            "shell",
            "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "
            + shell_quote(uri),
        ]

    @staticmethod
    def list_packages_args() -> list[str]:
        return ["shell", "pm", "list", "packages"]


def parse_adb_devices(output: str) -> list[AdbDevice]:
    devices: list[AdbDevice] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.lower().startswith("list of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append(AdbDevice(serial=parts[0], state=parts[1], details=" ".join(parts[2:])))
    return devices


class AdbClient:
    def __init__(self, adb_path: str | Path, runner: ProcessRunner | None = None) -> None:
        self.adb_path = str(adb_path)
        self.runner = runner or ProcessRunner()

    def run(self, args: Sequence[str], timeout: int = 30, device: str | None = None) -> CommandResult:
        final_args = [str(arg) for arg in args]
        if device and final_args and final_args[0] not in {"devices", "version", "connect", "disconnect"}:
            final_args = ["-s", device, *final_args]
        return self.runner.run(self.adb_path, final_args, timeout=timeout)

    def version(self) -> CommandResult:
        return self.run(["version"], timeout=10)

    def devices(self) -> tuple[list[AdbDevice], CommandResult]:
        result = self.run(["devices"], timeout=15)
        return parse_adb_devices(result.stdout), result

    def connect(self, host: str = DEFAULT_WSA_HOST, port: int = DEFAULT_WSA_PORT) -> CommandResult:
        return self.run(["connect", f"{host}:{port}"], timeout=20)

    def ensure_directory(self, remote_dir: str, device: str | None = None) -> CommandResult:
        return self.run(AdbCommandFactory.mkdir_args(remote_dir), timeout=20, device=device)

    def list_sdcard_dirs(self, device: str | None = None) -> CommandResult:
        return self.run(AdbCommandFactory.list_sdcard_dirs_args(), timeout=20, device=device)

    def push(self, local_path: str | Path, remote_path: str, device: str | None = None) -> CommandResult:
        return self.run(AdbCommandFactory.push_args(local_path, remote_path), timeout=180, device=device)

    def file_exists(self, remote_path: str, device: str | None = None) -> CommandResult:
        return self.run(AdbCommandFactory.ls_args(remote_path), timeout=20, device=device)

    def media_scan(self, remote_path: str, device: str | None = None) -> CommandResult:
        return self.run(AdbCommandFactory.media_scan_args(remote_path), timeout=20, device=device)

    def list_packages(self, device: str | None = None) -> CommandResult:
        return self.run(AdbCommandFactory.list_packages_args(), timeout=30, device=device)

    @staticmethod
    def choose_device(devices: Iterable[AdbDevice], preferred_serial: str) -> AdbDevice | None:
        device_list = list(devices)
        for device in device_list:
            if device.serial == preferred_serial:
                return device
        connected = [device for device in device_list if device.state == "device"]
        if len(connected) == 1:
            return connected[0]
        return None
