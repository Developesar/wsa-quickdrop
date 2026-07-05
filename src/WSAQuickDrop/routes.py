from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path, PurePosixPath

from . import DEFAULT_DESTINATION_ROOT


class DestinationMode(str, Enum):
    AUTO = "auto"
    PICTURES = "pictures"
    DOWNLOADS = "downloads"
    DOCUMENTS = "documents"
    MOVIES = "movies"
    MUSIC = "music"
    CUSTOM = "custom"


@dataclass(frozen=True)
class Route:
    category: str
    directory: str
    remote_path: str


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".heic", ".heif"}
PDF_EXTENSIONS = {".pdf"}
DOCUMENT_EXTENSIONS = {".txt", ".md", ".doc", ".docx", ".rtf", ".csv", ".json", ".xml"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}

AUTO_DIRECTORIES = {
    "image": f"/sdcard/Pictures/{DEFAULT_DESTINATION_ROOT}",
    "pdf": f"/sdcard/Download/{DEFAULT_DESTINATION_ROOT}",
    "document": f"/sdcard/Download/{DEFAULT_DESTINATION_ROOT}",
    "video": f"/sdcard/Movies/{DEFAULT_DESTINATION_ROOT}",
    "audio": f"/sdcard/Music/{DEFAULT_DESTINATION_ROOT}",
    "other": f"/sdcard/Download/{DEFAULT_DESTINATION_ROOT}",
}

MODE_DIRECTORIES = {
    DestinationMode.PICTURES: f"/sdcard/Pictures/{DEFAULT_DESTINATION_ROOT}",
    DestinationMode.DOWNLOADS: f"/sdcard/Download/{DEFAULT_DESTINATION_ROOT}",
    DestinationMode.DOCUMENTS: f"/sdcard/Documents/{DEFAULT_DESTINATION_ROOT}",
    DestinationMode.MOVIES: f"/sdcard/Movies/{DEFAULT_DESTINATION_ROOT}",
    DestinationMode.MUSIC: f"/sdcard/Music/{DEFAULT_DESTINATION_ROOT}",
}


class AndroidPathError(ValueError):
    pass


def normalize_mode(value: str | DestinationMode | None) -> DestinationMode:
    if isinstance(value, DestinationMode):
        return value
    if not value:
        return DestinationMode.AUTO
    lowered = value.strip().lower()
    try:
        return DestinationMode(lowered)
    except ValueError as exc:
        allowed = ", ".join(mode.value for mode in DestinationMode)
        raise ValueError(f"Unknown target '{value}'. Expected one of: {allowed}") from exc


def classify_file(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in PDF_EXTENSIONS:
        return "pdf"
    if suffix in DOCUMENT_EXTENSIONS:
        return "document"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    return "other"


def validate_android_directory(path: str) -> str:
    candidate = (path or "").strip().replace("\\", "/")
    if not candidate:
        raise AndroidPathError("Android path cannot be empty.")
    if not candidate.startswith("/sdcard/"):
        raise AndroidPathError("Custom Android paths must start with /sdcard/.")
    if candidate in {"/", "/sdcard", "/sdcard/"}:
        raise AndroidPathError("Choose a directory below /sdcard/, not the storage root.")
    if any(ord(char) < 32 for char in candidate):
        raise AndroidPathError("Android path cannot contain control characters.")
    parts = PurePosixPath(candidate).parts
    if ".." in parts:
        raise AndroidPathError("Android path cannot contain '..'.")
    blocked = {"/system", "/data", "/vendor", "/proc", "/dev", "/"}
    if candidate.rstrip("/") in blocked:
        raise AndroidPathError("That Android path is not allowed.")
    normalized = "/" + str(PurePosixPath(candidate)).lstrip("/")
    if not normalized.startswith("/sdcard/"):
        raise AndroidPathError("Custom Android paths must stay under /sdcard/.")
    return normalized.rstrip("/")


def safe_remote_filename(path: str | Path) -> str:
    name = Path(path).name.strip()
    if not name:
        name = "quickdrop-file"
    name = name.replace("/", "_").replace("\\", "_")
    name = "".join("_" if ord(char) < 32 else char for char in name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    if name in {"", ".", ".."}:
        return "quickdrop-file"
    if ".." in PurePosixPath(name).parts:
        return name.replace("..", "__")
    return name


def append_timestamp_to_name(filename: str, now: datetime | None = None) -> str:
    current = now or datetime.now()
    stamp = current.strftime("%Y%m%d-%H%M%S")
    path = Path(filename)
    suffix = path.suffix
    stem = filename[: -len(suffix)] if suffix else filename
    if not stem:
        stem = "quickdrop-file"
    return f"{stem}-{stamp}{suffix}"


def join_android_path(directory: str, filename: str) -> str:
    safe_dir = validate_android_directory(directory)
    safe_name = safe_remote_filename(filename)
    if safe_name in {".", ".."} or "/" in safe_name:
        raise AndroidPathError("Remote filename is not safe.")
    return f"{safe_dir}/{safe_name}"


def route_for_file(
    path: str | Path,
    mode: str | DestinationMode = DestinationMode.AUTO,
    custom_path: str | None = None,
    append_timestamp: bool = False,
    now: datetime | None = None,
) -> Route:
    destination_mode = normalize_mode(mode)
    category = classify_file(path)
    if destination_mode == DestinationMode.AUTO:
        directory = AUTO_DIRECTORIES[category]
    elif destination_mode == DestinationMode.CUSTOM:
        if not custom_path:
            raise AndroidPathError("Custom target selected, but no custom Android path was provided.")
        directory = validate_android_directory(custom_path)
    else:
        directory = MODE_DIRECTORIES[destination_mode]
    filename = safe_remote_filename(path)
    if append_timestamp:
        filename = append_timestamp_to_name(filename, now=now)
    return Route(category=category, directory=directory, remote_path=join_android_path(directory, filename))


def human_file_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
