"""Configuration constants for GameTimeTracker."""

import os

APP_NAME = "GameTimeTracker"

# Polling interval in seconds
POLLING_INTERVAL_SECONDS = float(os.getenv("GTT_POLL_SEC", "10"))
