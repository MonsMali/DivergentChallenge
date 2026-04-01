"""Shared fixtures for integration tests."""

import os
from pathlib import Path

import pytest

from src.orchestrator import load_data


def _has_gdrive_credentials() -> bool:
    """Check whether Google Drive credentials are available."""
    if os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
        return True
    if Path("credentials.json").exists():
        return True
    return False


requires_gdrive = pytest.mark.skipif(
    not _has_gdrive_credentials(),
    reason="Google Drive credentials not configured, skipping integration tests",
)


@pytest.fixture(scope="session")
def ingested_data():
    """Download data from Google Drive and ingest it once for the entire test session."""
    if not _has_gdrive_credentials():
        pytest.skip("Google Drive credentials not configured, skipping integration tests")
    return load_data()
