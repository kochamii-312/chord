"""Utilities for persisting image and task set configurations.

This module centralises the read/write logic so that multiple Streamlit pages
can share the same storage format.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlparse

_DATA_PATH = Path("json/image_task_sets.json")
_PROJECT_ROOT = Path(__file__).resolve().parent


def load_image_task_sets() -> Dict[str, Dict[str, Any]]:
    """Load all stored image/task sets.

    Returns an empty dictionary when the storage file does not exist or is
    malformed. The function is resilient to partial corruption and will ignore
    entries that are not dictionaries.
    """

    if not _DATA_PATH.exists():
        return {}

    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(raw, dict):
        return {}

    cleaned: Dict[str, Dict[str, Any]] = {}
    for key, value in raw.items():
        if isinstance(value, dict):
            cleaned[str(key)] = value
    return cleaned


def save_image_task_sets(task_sets: Dict[str, Dict[str, Any]]) -> None:
    """Persist the provided task sets to disk."""

    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DATA_PATH.write_text(
        json.dumps(task_sets, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_image_task_set(name: str, payload: Dict[str, Any]) -> None:
    """Create or update a single task set entry."""

    task_sets = load_image_task_sets()
    task_sets[name] = payload
    save_image_task_sets(task_sets)


def delete_image_task_set(name: str) -> None:
    """Remove a task set from storage if it exists."""

    task_sets = load_image_task_sets()
    if name in task_sets:
        task_sets.pop(name)
        save_image_task_sets(task_sets)

def extract_task_lines(payload: Dict[str, Any]) -> List[str]:
    """Return a list of task strings from a payload."""

    tasks: List[str] = []
    if not isinstance(payload, dict):
        return tasks

    value = payload.get("tasks")
    if isinstance(value, list):
        tasks = [str(item).strip() for item in value if str(item).strip()]
    elif isinstance(value, str):
        tasks = [line.strip() for line in value.splitlines() if line.strip()]
    else:
        raw_text = payload.get("task_text")
        if isinstance(raw_text, str):
            tasks = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return tasks


def derive_task_set_label(name: str, payload: Dict[str, Any]) -> str:
    """Create a human-readable label for a stored task set."""

    task_lines = extract_task_lines(payload)
    if task_lines:
        label = task_lines[0]
    else:
        label = name.strip()

    label = label.replace("\n", " / ").strip()
    return label or "(タスク未設定)"


def build_task_set_choices(
    task_sets: Dict[str, Dict[str, Any]]
) -> List[Tuple[str, str]]:
    """Return (label, key) tuples for select boxes."""

    choices: List[Tuple[str, str]] = []
    counts: Dict[str, int] = {}
    for key, payload in task_sets.items():
        base_label = derive_task_set_label(key, payload)
        counts[base_label] = counts.get(base_label, 0) + 1
        suffix = "" if counts[base_label] == 1 else f" ({counts[base_label]})"
        display_label = f"{base_label}{suffix}"
        choices.append((display_label, key))

    choices.sort(key=lambda item: item[0])
    return choices


def is_web_url(path_str: str) -> bool:
    """Return True if ``path_str`` looks like a HTTP(S) URL."""

    try:
        scheme = urlparse(str(path_str)).scheme.lower()
    except ValueError:
        return False
    return scheme in {"http", "https"}


def resolve_image_path(path_str: str) -> Path:
    """Return a Path object that best matches the stored path string.

    The saved image paths are typically relative to the project root.  However,
    depending on how Streamlit is executed (e.g. from a different working
    directory on Google Cloud), simple string checks with ``os.path.exists`` can
    fail.  This helper attempts a handful of sensible fallbacks so callers can
    reliably locate the image files regardless of the current working
    directory.
    """

    # ``path_str`` may come from Windows environments where the path was saved
    # with backslashes (e.g. ``images\house2\LIVING\00051-rgb.png``).  On
    # Linux these backslashes are treated as literal characters which prevents
    # ``Path`` from resolving the file correctly.  Normalise the separators
    # before constructing the ``Path`` object so the resolution logic works
    # irrespective of the originating platform.
    normalised = str(path_str).replace("\\", "/")
    original = Path(normalised)
    candidates = [original]

    if not original.is_absolute():
        candidates.append((_PROJECT_ROOT / original).resolve())

    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue

    return candidates[-1]


def resolve_image_paths(paths: Iterable[str]) -> Tuple[List[str], List[str]]:
    """Resolve a collection of image paths or URLs.

    Returns a tuple of ``(existing, missing)`` where ``existing`` contains
    local filesystem paths or HTTP(S) URLs that are available to Streamlit and
    ``missing`` contains the original strings that could not be resolved.
    """

    existing: List[str] = []
    missing: List[str] = []

    for path_str in paths:
        if is_web_url(path_str):
            existing.append(str(path_str))
            continue
        resolved = resolve_image_path(path_str)
        if resolved.exists():
            existing.append(str(resolved))
        else:
            missing.append(str(path_str))

    return existing, missing

