from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Sequence


CREATE_NO_WINDOW = 0x08000000


@dataclass(frozen=True)
class CommandResult:
    executable: str
    args: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_seconds: float

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out

    @property
    def command_for_log(self) -> str:
        return " ".join([self.executable, *self.args])


class ProcessRunner:
    def run(self, executable: str, args: Sequence[str], timeout: int = 30) -> CommandResult:
        start = time.monotonic()
        command = [str(executable), *[str(arg) for arg in args]]
        try:
            completed = subprocess.run(
                command,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
                shell=False,
                creationflags=CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            return CommandResult(
                executable=str(executable),
                args=[str(arg) for arg in args],
                returncode=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
                timed_out=False,
                duration_seconds=time.monotonic() - start,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                executable=str(executable),
                args=[str(arg) for arg in args],
                returncode=124,
                stdout=(exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "").strip() if isinstance(exc.stderr, str) else "Command timed out.",
                timed_out=True,
                duration_seconds=time.monotonic() - start,
            )
        except OSError as exc:
            return CommandResult(
                executable=str(executable),
                args=[str(arg) for arg in args],
                returncode=127,
                stdout="",
                stderr=str(exc),
                timed_out=False,
                duration_seconds=time.monotonic() - start,
            )
