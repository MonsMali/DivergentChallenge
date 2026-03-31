"""Google Drive data source using a service account.

Setup instructions:
  1. Create a GCP project at https://console.cloud.google.com
  2. Enable the Google Drive API
  3. Create a service account (IAM & Admin > Service Accounts)
  4. Download the JSON credentials file
  5. Share the target Drive folder with the service account email address
  6. Set GOOGLE_SERVICE_ACCOUNT_JSON env var to the JSON string,
     or place credentials.json in the project root.
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from src.config import GOOGLE_SERVICE_ACCOUNT_JSON

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _get_credentials(credentials_path: str) -> service_account.Credentials:
    """Load service account credentials from env var or file."""
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    creds_file = Path(credentials_path)
    if not creds_file.exists():
        raise FileNotFoundError(
            f"No credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON env var "
            f"or place a credentials file at {creds_file.resolve()}"
        )
    return service_account.Credentials.from_service_account_file(str(creds_file), scopes=SCOPES)


def _list_files_recursive(service, folder_id: str) -> list[dict]:
    """List all non-folder files under folder_id, recursing into subfolders."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get("files", [])

    files = []
    for item in items:
        if item["mimeType"] == "application/vnd.google-apps.folder":
            files.extend(_list_files_recursive(service, item["id"]))
        else:
            files.append(item)
    return files


def load_from_gdrive(
    folder_id: str,
    credentials_path: str = "credentials.json",
) -> str:
    """Download all files from a Google Drive folder to a temp directory.

    Returns the path to the temp directory containing the downloaded files.
    """
    creds = _get_credentials(credentials_path)
    service = build("drive", "v3", credentials=creds)

    # Collect all downloadable files, recursing into subfolders
    downloadable = _list_files_recursive(service, folder_id)

    if not downloadable:
        raise ValueError(f"No files found in Drive folder {folder_id}")

    # Export mime mappings for Google Workspace files
    export_map = {
        "application/vnd.google-apps.spreadsheet": ("text/csv", ".csv"),
        "application/vnd.google-apps.document": ("text/plain", ".txt"),
    }

    # Download each file to a temp directory
    tmp_dir = tempfile.mkdtemp(prefix="revops_")
    logger.info("Downloading %d files from Drive to %s", len(downloadable), tmp_dir)

    for file_meta in downloadable:
        file_id = file_meta["id"]
        file_name = file_meta["name"]
        mime_type = file_meta.get("mimeType", "")

        if mime_type in export_map:
            # Google Workspace file — must export, not download
            export_mime, ext = export_map[mime_type]
            if not file_name.endswith(ext):
                file_name += ext
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            # Regular binary file — direct download
            request = service.files().get_media(fileId=file_id)

        dest_path = Path(tmp_dir) / file_name
        with open(dest_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        logger.info("Downloaded: %s", file_name)

    return tmp_dir
