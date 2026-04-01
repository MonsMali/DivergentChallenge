"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
DEFAULT_MODEL: str = "claude-sonnet-4-6"
FAST_MODEL: str = "claude-haiku-4-5-20251001"
DEFAULT_GDRIVE_FOLDER_ID: str = os.getenv(
    "GDRIVE_FOLDER_ID", "1CjyUQgtfl0AKEXBhkS7pxuEEs1UWn1ud"
)
