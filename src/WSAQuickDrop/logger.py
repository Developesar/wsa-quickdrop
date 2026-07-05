from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from . import APP_VERSION


class LocalLogger:
    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            appdata = os.environ.get("APPDATA")
            base_dir = (Path(appdata) if appdata else Path.home()) / "WSAQuickDrop" / "logs"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d")
        self.path = self.base_dir / f"wsa-quickdrop-{stamp}.log"

    def write(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def start_session(self) -> None:
        self.write(f"WSA QuickDrop {APP_VERSION} session started")
