"""Local filesystem data source."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

EXPECTED_FILES = ["accounts.csv", "deals.csv", "activities.csv", "call_notes.txt"]


def load_from_local(data_dir: str) -> str:
    """Validate local data directory and return its path.

    Warns if expected files are missing but does not crash.
    """
    path = Path(data_dir).resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {path}")

    for fname in EXPECTED_FILES:
        if not (path / fname).exists():
            logger.warning("Expected file missing: %s", fname)

    logger.info("Using local data source: %s", path)
    return str(path)
