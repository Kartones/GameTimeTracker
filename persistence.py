"""File I/O and data persistence operations."""

import datetime as dt
import json
import os
import sys
from pathlib import Path

from config import APP_NAME


def user_data_dir() -> Path:
    """Return cross-platform user data directory for the application."""
    if sys.platform == "win32":
        base = os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming"
        return Path(base) / APP_NAME
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        return Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME


def load_exclusions(data_dir: Path) -> list[str]:
    """Load exclusion substrings from exclusions.json in user data directory."""
    exclusions_file = data_dir / "exclusions.json"
    if exclusions_file.exists():
        try:
            data = json.loads(exclusions_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [s.lower() for s in data if isinstance(s, str) and s]
        except Exception:
            pass
    return []


def load_aliases(data_dir: Path) -> dict[str, str]:
    """Load application name aliases from aliases.json in user data directory."""
    aliases_file = data_dir / "aliases.json"
    if aliases_file.exists():
        try:
            data = json.loads(aliases_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {k.lower(): v.lower() for k, v in data.items() if isinstance(k, str) and isinstance(v, str) and k and v}
        except Exception:
            pass
    return {}


def day_file_path(day: dt.date, data_dir: Path) -> Path:
    """Return the file path for a given day's tracking data."""
    return data_dir / f"{day.isoformat()}.json"


def load_day_totals(day: dt.date, data_dir: Path) -> dict[str, int]:
    """Load time totals for a given day."""
    path = day_file_path(day, data_dir)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            # Corrupt? Start fresh but keep a backup
            path.rename(path.with_suffix(".corrupt.json"))
    return {}


def atomic_write_json(path: Path, json_object: dict[str, int]) -> None:
    """
    Atomically write a dictionary to JSON file.
    Rounds float values up to integers before saving.
    """
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(json_object, ensure_ascii=False, indent=0), encoding="utf-8")
    tmp.replace(path)
