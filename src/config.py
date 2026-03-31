"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
