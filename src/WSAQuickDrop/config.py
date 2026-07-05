from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from . import DEFAULT_WSA_HOST, DEFAULT_WSA_PORT
from .android_folders import selected_folder_from_config


@dataclass
class AppConfig:
    adbPath: str = ""
    wsaHost: str = DEFAULT_WSA_HOST
    wsaPort: int = DEFAULT_WSA_PORT
    defaultRouteMode: str = "auto"
    lastDestination: str = ""
    lastSelectedAndroidFolder: str = "/sdcard/Pictures"
    lastSelectedFriendlyFolder: str = "Pictures"
    autoMediaScan: bool = True
    closeAfterSend: bool = False
    openAfterSend: bool = False
    sendImmediatelyFromSendTo: bool = False
    showAdvancedPaths: bool = False
    windowGeometry: str = ""
    theme: str = "system"
    language: str = "en"
    optionalTargetAppPackage: str = ""
    appendTimestampOnCollision: bool = False

    @staticmethod
    def config_dir(base: Path | None = None) -> Path:
        if base is not None:
            return base
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "WSAQuickDrop"
        return Path.home() / ".WSAQuickDrop"

    @staticmethod
    def config_path(base: Path | None = None) -> Path:
        return AppConfig.config_dir(base) / "config.json"

    @classmethod
    def load(cls, base: Path | None = None) -> "AppConfig":
        path = cls.config_path(base)
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        defaults = asdict(cls())
        merged = {**defaults, **{key: data.get(key, defaults[key]) for key in defaults}}
        try:
            merged["wsaPort"] = int(merged["wsaPort"])
        except (TypeError, ValueError):
            merged["wsaPort"] = DEFAULT_WSA_PORT
        selected = selected_folder_from_config(
            str(merged.get("lastSelectedAndroidFolder") or ""),
            str(merged.get("lastSelectedFriendlyFolder") or ""),
            str(merged.get("lastDestination") or ""),
        )
        merged["lastSelectedAndroidFolder"] = selected.android_path
        merged["lastSelectedFriendlyFolder"] = selected.friendly_path
        return cls(**merged)

    def save(self, base: Path | None = None) -> Path:
        folder = self.config_dir(base)
        folder.mkdir(parents=True, exist_ok=True)
        path = self.config_path(base)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def parse_endpoint(value: str | None, default_host: str = DEFAULT_WSA_HOST, default_port: int = DEFAULT_WSA_PORT) -> tuple[str, int]:
    if not value:
        return default_host, default_port
    text = value.strip()
    if ":" not in text:
        return text, default_port
    host, port_text = text.rsplit(":", 1)
    return host or default_host, int(port_text)
