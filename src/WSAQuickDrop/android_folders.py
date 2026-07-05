from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from .routes import AndroidPathError, validate_android_directory


ROOT_LABEL = "Pixel 5"
ROOT_PATH = "/sdcard"
DEFAULT_ANDROID_FOLDER = "/sdcard/Pictures"
DEFAULT_FRIENDLY_FOLDER = "Pictures"

BUILTIN_FOLDERS = ["Pictures", "Download", "Documents", "DCIM", "Movies", "Music", "Ringtones"]

FOLDER_ALIASES = {
    "picture": "Pictures",
    "pictures": "Pictures",
    "download": "Download",
    "downloads": "Download",
    "document": "Documents",
    "documents": "Documents",
    "dcim": "DCIM",
    "movie": "Movies",
    "movies": "Movies",
    "music": "Music",
    "ringtone": "Ringtones",
    "ringtones": "Ringtones",
}


@dataclass(frozen=True)
class AndroidFolder:
    friendly_path: str
    android_path: str
    depth: int = 1
    builtin: bool = False

    @property
    def display_name(self) -> str:
        return self.friendly_path.split("/")[-1]


class FolderNameError(ValueError):
    pass


def validate_folder_name(name: str) -> str:
    original = name or ""
    if original.strip() != original:
        raise FolderNameError("Folder name cannot start or end with whitespace.")
    if any(ord(char) < 32 for char in original):
        raise FolderNameError("Folder name cannot contain control characters.")
    cleaned = re.sub(r"\s+", " ", original)
    if not cleaned:
        raise FolderNameError("Folder name cannot be empty.")
    if "/" in cleaned or "\\" in cleaned:
        raise FolderNameError("Folder name cannot contain slashes.")
    if cleaned in {".", ".."} or ".." in cleaned:
        raise FolderNameError("Folder name cannot contain '..'.")
    if cleaned.rstrip(" .") != cleaned:
        raise FolderNameError("Folder name cannot end with a dot or space.")
    return cleaned


def normalize_friendly_part(part: str) -> str:
    cleaned = validate_folder_name(part)
    return FOLDER_ALIASES.get(cleaned.casefold(), cleaned)


def normalize_friendly_path(value: str) -> str:
    text = (value or "").strip().replace("\\", "/").strip("/")
    parts = [normalize_friendly_part(part) for part in text.split("/") if part.strip()]
    if not parts:
        raise FolderNameError("Folder path cannot be empty.")
    return "/".join(parts)


def friendly_to_android_path(value: str) -> str:
    text = (value or "").strip().replace("\\", "/")
    if not text:
        raise AndroidPathError("Choose an Android folder before sending.")
    if text == ROOT_LABEL:
        raise AndroidPathError("Choose a folder inside Pixel 5, not the Pixel 5 root.")
    if text.startswith("/sdcard/"):
        return validate_android_directory(text)
    if text.startswith("/"):
        raise AndroidPathError("Only folders inside Pixel 5 are supported.")
    try:
        friendly_path = normalize_friendly_path(text)
    except FolderNameError as exc:
        raise AndroidPathError(str(exc)) from exc
    return validate_android_directory(ROOT_PATH + "/" + friendly_path)


def friendly_from_android_path(path: str) -> str:
    normalized = validate_android_directory(path)
    relative = normalized.removeprefix(ROOT_PATH + "/")
    if not relative:
        return ROOT_LABEL
    return relative


def build_child_folder_path(parent_android_path: str, folder_name: str) -> tuple[str, str]:
    parent = validate_android_directory(parent_android_path)
    child = validate_folder_name(folder_name)
    android_path = validate_android_directory(f"{parent}/{child}")
    return friendly_from_android_path(android_path), android_path


def parse_ls_directories(output: str) -> list[str]:
    folders: list[str] = []
    seen: set[str] = set()
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("ls:") or "Permission denied" in line:
            continue
        if line.startswith(ROOT_PATH + "/"):
            line = line.removeprefix(ROOT_PATH + "/")
        if line.endswith("/"):
            name = line[:-1].strip()
        else:
            # Some Android toybox builds omit -p markers for directories when aliases are involved.
            name = line.strip()
        if not name or name in {".", ".."}:
            continue
        try:
            safe_name = normalize_friendly_path(name)
        except FolderNameError:
            continue
        key = safe_name.casefold()
        if key not in seen:
            folders.append(safe_name)
            seen.add(key)
    return folders


def merge_builtin_and_discovered(discovered_names: list[str]) -> list[AndroidFolder]:
    names: list[str] = []
    seen: set[str] = set()
    for name in [*BUILTIN_FOLDERS, *discovered_names]:
        try:
            safe_name = normalize_friendly_path(name)
        except FolderNameError:
            continue
        key = safe_name.casefold()
        if key in seen:
            continue
        names.append(safe_name)
        seen.add(key)
    return [
        AndroidFolder(
            friendly_path=name,
            android_path=friendly_to_android_path(name),
            depth=len(name.split("/")),
            builtin=name in BUILTIN_FOLDERS,
        )
        for name in names
    ]


def selected_folder_from_config(last_android_folder: str = "", last_friendly_folder: str = "", legacy_destination: str = "") -> AndroidFolder:
    for candidate in (last_android_folder, legacy_destination):
        if not candidate:
            continue
        try:
            android_path = friendly_to_android_path(candidate)
            return AndroidFolder(friendly_from_android_path(android_path), android_path)
        except (AndroidPathError, FolderNameError):
            continue
    if last_friendly_folder:
        try:
            android_path = friendly_to_android_path(last_friendly_folder)
            return AndroidFolder(friendly_from_android_path(android_path), android_path)
        except (AndroidPathError, FolderNameError):
            pass
    return AndroidFolder(DEFAULT_FRIENDLY_FOLDER, DEFAULT_ANDROID_FOLDER, builtin=True)


def folder_sort_key(folder: AndroidFolder) -> tuple[int, str]:
    try:
        builtin_index = BUILTIN_FOLDERS.index(folder.friendly_path.split("/")[0])
    except ValueError:
        builtin_index = len(BUILTIN_FOLDERS)
    return builtin_index, folder.friendly_path.casefold()
