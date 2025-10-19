#!/usr/bin/env python3
"""Export game time data to FG format."""

import datetime as dt
import json
import sys
from pathlib import Path

from persistence import user_data_dir
from time_utils import today_local

LAST_EXPORT_FILE = "last_export_ts"


def _load_last_export_ts(data_dir: Path) -> dt.date:
    """Load last export timestamp from file, or return 1970-01-01 if not present."""
    last_export_file = data_dir / LAST_EXPORT_FILE

    if last_export_file.exists():
        try:
            content = last_export_file.read_text(encoding="utf-8").strip()
            return dt.datetime.strptime(content, "%Y-%m-%d").date()
        except Exception:
            pass

    return dt.date(1970, 1, 1)


def _gather_game_time_data(data_dir: Path, start_date: dt.date) -> dict[str, int]:
    """
    Gather all game time data from files after start_date.
    Aggregates values for duplicate keys.
    """
    aggregated: dict[str, int] = {}

    # Iterate through all .json files in data_dir
    for json_file in sorted(data_dir.glob("*.json")):
        # Skip non-date files (like aliases.json, exclusions.json, etc.)
        try:
            file_date = dt.datetime.strptime(json_file.stem, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Only process files after start_date
        if file_date <= start_date:
            continue

        print(f"Processing {json_file.name}")
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        # just in case, lowercase
                        game_title = str(key).lower()
                        aggregated[game_title] = aggregated.get(game_title, 0) + int(value)
        except Exception as e:
            print(f"  Warning: could not read {json_file.name}: {e}")

    return aggregated


def _export_to_files(data_dir: Path, output_base: str, data: dict[str, int]) -> None:
    """
    Write aggregated data to .input and .output files in data_dir.
    """
    input_file = data_dir / (Path(output_base).name + ".input")
    output_file = data_dir / (Path(output_base).name + ".output")

    sorted_keys = sorted(data.keys())

    input_lines = [key for key in sorted_keys]
    input_file.write_text("\n".join(input_lines), encoding="utf-8")

    output_lines = []
    for key in sorted_keys:
        seconds = data[key]
        minutes = round(seconds / 60)
        output_lines.append(str(minutes))
        print(f"  {key}: {seconds}s → {minutes}min")

    output_file.write_text("\n".join(output_lines), encoding="utf-8")

    print(f"\nExported to:")
    print(f"  {input_file}")
    print(f"  {output_file}")


def _save_last_export_ts(data_dir: Path) -> None:
    """Save current date as last export timestamp."""
    last_export_file = data_dir / LAST_EXPORT_FILE
    today = today_local()
    last_export_file.write_text(today.isoformat(), encoding="utf-8")
    print(f"Saved last export timestamp: {today.isoformat()}")


def main():
    if len(sys.argv) < 2:
        print("Usage: export_to_fg_game_time.py <output_base>")
        print("  Exports to <output_base>.input and <output_base>.output")
        sys.exit(1)

    output_base = sys.argv[1]
    data_dir = user_data_dir()

    last_export = _load_last_export_ts(data_dir)
    print(f"Loading files after: {last_export.isoformat()}\n")

    data = _gather_game_time_data(data_dir, last_export)
    if not data:
        print("No data to export")
    else:
        _export_to_files(data_dir, output_base, data)

    _save_last_export_ts(data_dir)


if __name__ == "__main__":
    main()
