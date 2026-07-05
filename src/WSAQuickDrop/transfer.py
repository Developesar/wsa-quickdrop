from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from . import DEFAULT_WSA_HOST, DEFAULT_WSA_PORT
from .adb import AdbClient, AdbDevice, AdbDiscovery
from .config import AppConfig
from .logger import LocalLogger
from .routes import AndroidPathError, Route, route_for_file

StatusCallback = Callable[["TransferItem"], None]


@dataclass
class TransferOptions:
    target: str = "auto"
    custom_path: str = ""
    adb_path: str = ""
    host: str = DEFAULT_WSA_HOST
    port: int = DEFAULT_WSA_PORT
    scan: bool = True
    append_timestamp: bool = False
    verbose: bool = False


@dataclass
class TransferItem:
    local_path: str
    category: str = ""
    remote_dir: str = ""
    remote_path: str = ""
    status: str = "queued"
    message: str = ""


@dataclass
class TransferSummary:
    items: list[TransferItem] = field(default_factory=list)
    adb_path: str = ""
    device: str = ""
    messages: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.items) and all(item.status in {"sent", "scanned"} for item in self.items)


class TransferService:
    def __init__(
        self,
        config: AppConfig | None = None,
        logger: LocalLogger | None = None,
        client: AdbClient | None = None,
        discovery: AdbDiscovery | None = None,
    ) -> None:
        self.config = config or AppConfig.load()
        self.logger = logger or LocalLogger()
        self.client = client
        self.discovery = discovery or AdbDiscovery()

    def discover_adb(self, override: str = "") -> Path | None:
        return self.discovery.find_adb(override or self.config.adbPath)

    def ensure_connection(self, options: TransferOptions) -> tuple[AdbClient | None, AdbDevice | None, list[str]]:
        messages: list[str] = []
        adb_path = Path(options.adb_path) if options.adb_path else self.discover_adb()
        if self.client is not None:
            client = self.client
            adb_path = Path(client.adb_path)
        elif adb_path is not None:
            client = AdbClient(adb_path)
        else:
            return None, None, ["adb.exe was not found. Open docs/ADB_SETUP_EN.md or choose adb.exe manually."]

        preferred = f"{options.host}:{options.port}"
        devices, result = client.devices()
        self._log_result("adb devices", result)
        if not result.ok:
            messages.append(result.stderr or result.stdout or "adb devices failed.")

        chosen = client.choose_device(devices, preferred)
        if chosen is None or chosen.state != "device":
            connect_result = client.connect(options.host, options.port)
            self._log_result(f"adb connect {preferred}", connect_result)
            messages.append(connect_result.stdout or connect_result.stderr or f"Tried adb connect {preferred}.")
            devices, result = client.devices()
            self._log_result("adb devices recheck", result)
            chosen = client.choose_device(devices, preferred)

        if chosen is None:
            if devices:
                states = ", ".join(f"{device.serial}={device.state}" for device in devices)
                messages.append(f"Could not choose a target device. Devices: {states}")
            else:
                messages.append("No ADB devices are connected. Start WSA and enable Developer Mode.")
            return client, None, messages
        if chosen.state == "offline":
            messages.append(f"Device {chosen.serial} is offline. Restart WSA or reconnect ADB.")
            return client, chosen, messages
        if chosen.state == "unauthorized":
            messages.append(f"Device {chosen.serial} is unauthorized. Confirm the ADB prompt in Android if shown.")
            return client, chosen, messages
        if chosen.state != "device":
            messages.append(f"Device {chosen.serial} is in state '{chosen.state}', not ready.")
            return client, chosen, messages
        messages.append(f"Using ADB device {chosen.serial}.")
        return client, chosen, messages

    def send_files(
        self,
        files: Iterable[str | Path],
        options: TransferOptions,
        callback: StatusCallback | None = None,
    ) -> TransferSummary:
        self.logger.start_session()
        summary = TransferSummary()
        client, device, messages = self.ensure_connection(options)
        summary.messages.extend(messages)
        summary.adb_path = client.adb_path if client else ""
        summary.device = device.serial if device else ""
        for message in messages:
            self.logger.write(message)

        file_list = [Path(file) for file in files]
        self.logger.write(f"Selected file count: {len(file_list)}")

        if client is None or device is None or device.state != "device":
            for file in file_list:
                item = TransferItem(local_path=str(file), status="failed", message="ADB/WSA connection is not ready.")
                summary.items.append(item)
                self._notify(callback, item)
            return summary

        for file in file_list:
            item = TransferItem(local_path=str(file))
            summary.items.append(item)
            self._notify(callback, item)
            try:
                if not file.is_file():
                    raise FileNotFoundError(f"Local file does not exist: {file}")
                route = route_for_file(
                    file,
                    mode=options.target,
                    custom_path=options.custom_path,
                    append_timestamp=options.append_timestamp,
                )
                self._fill_route(item, route)
                item.status = "sending"
                item.message = "Creating Android destination."
                self._notify(callback, item)
                mkdir_result = client.ensure_directory(route.directory, device=device.serial)
                self._log_result(f"mkdir {route.directory}", mkdir_result)
                if not mkdir_result.ok:
                    raise RuntimeError(mkdir_result.stderr or mkdir_result.stdout or "Failed to create Android directory.")

                item.message = "Pushing file with adb."
                self._notify(callback, item)
                push_result = client.push(file, route.remote_path, device=device.serial)
                self._log_result(f"push {file} -> {route.remote_path}", push_result)
                if not push_result.ok:
                    raise RuntimeError(push_result.stderr or push_result.stdout or "adb push failed.")

                item.message = "Verifying remote file."
                self._notify(callback, item)
                verify_result = client.file_exists(route.remote_path, device=device.serial)
                self._log_result(f"ls {route.remote_path}", verify_result)
                if not verify_result.ok:
                    raise RuntimeError(verify_result.stderr or verify_result.stdout or "Remote file verification failed.")

                item.status = "sent"
                item.message = "Sent."
                self._notify(callback, item)

                if options.scan:
                    item.status = "scanned"
                    item.message = "Triggering Android media scanner."
                    self._notify(callback, item)
                    scan_result = client.media_scan(route.remote_path, device=device.serial)
                    self._log_result(f"media scan {route.remote_path}", scan_result)
                    if scan_result.ok:
                        item.message = "Sent and media scan requested."
                    else:
                        item.message = "Sent, but media scan did not confirm. Refresh the Android file picker."
                    self._notify(callback, item)
            except (AndroidPathError, FileNotFoundError, RuntimeError) as exc:
                item.status = "failed"
                item.message = str(exc)
                self.logger.write(f"Failed: {file}: {exc}")
                self._notify(callback, item)
        return summary

    def check_package_installed(self, package_ids: Iterable[str], options: TransferOptions) -> tuple[bool, str]:
        client, device, messages = self.ensure_connection(options)
        if client is None or device is None:
            return False, "\n".join(messages)
        result = client.list_packages(device=device.serial)
        self._log_result("pm list packages", result)
        if not result.ok:
            return False, result.stderr or result.stdout
        package_set = {line.replace("package:", "").strip() for line in result.stdout.splitlines()}
        for package_id in package_ids:
            if package_id in package_set:
                return True, package_id
        return False, "Package not found."

    def _fill_route(self, item: TransferItem, route: Route) -> None:
        item.category = route.category
        item.remote_dir = route.directory
        item.remote_path = route.remote_path

    def _notify(self, callback: StatusCallback | None, item: TransferItem) -> None:
        if callback:
            callback(item)

    def _log_result(self, label: str, result) -> None:
        self.logger.write(
            f"{label}: exit={result.returncode} timeout={result.timed_out} "
            f"stdout={result.stdout[:400]!r} stderr={result.stderr[:400]!r}"
        )
