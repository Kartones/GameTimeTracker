#!/usr/bin/env python3
"""Main entry point for GameTimeTracker."""

import math
import time

from app_identifier import list_running_identities
from config import APP_NAME, POLLING_INTERVAL_SECONDS
from persistence import (
    atomic_write_json,
    day_file_path,
    load_aliases,
    load_day_totals,
    load_exclusions,
    user_data_dir,
)
from time_utils import today_local


def main():
    data_dir = user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    exclude_substrings = load_exclusions(data_dir)
    aliases = load_aliases(data_dir)
    print(f"[{APP_NAME}]: loaded {len(exclude_substrings)} exclusions and {len(aliases)} aliases")
    print(f"[{APP_NAME}]: polling every {POLLING_INTERVAL_SECONDS:.2f}s; data dir: {data_dir}")
    print(f"[{APP_NAME}]: Press Ctrl+C to stop")

    # We don't care if the day changes while running
    current_day = today_local()
    totals = load_day_totals(current_day, data_dir)
    last_monotonic = time.monotonic()

    try:
        while True:
            time.sleep(POLLING_INTERVAL_SECONDS)
            now_mono = time.monotonic()
            elapsed = math.ceil(max(0.0, now_mono - last_monotonic))

            running = list_running_identities(exclude_substrings, aliases)
            if running:
                for identity in running:
                    totals[identity] = totals.get(identity, 0) + elapsed
                atomic_write_json(day_file_path(current_day, data_dir), totals)

            last_monotonic = now_mono
    except KeyboardInterrupt:
        # Do a final flush
        atomic_write_json(day_file_path(current_day, data_dir), totals)
        print(f"\n[{APP_NAME}]: Stopped. Data saved.")


if __name__ == "__main__":
    main()
