"""
PDF service — downloads PDFs from a Google Drive folder and extracts their text.

The folder is set via FUND2_DRIVE_FOLDER_ID env var. Share the folder with
the service account email and drop any PDFs there; restart the server to reload.

Text is extracted once at first use and cached for the server session.
"""

import io
from typing import Optional

import pdfplumber
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class PDFService:
    def __init__(self):
        self._cached_text: Optional[str] = None

    def _drive(self):
        credentials = Credentials.from_service_account_file(
            settings.google_credentials_file, scopes=_SCOPES
        )
        return build("drive", "v3", credentials=credentials, cache_discovery=False)

    def get_document_context(self) -> Optional[str]:
        """
        Download all PDFs from the configured Drive folder, extract their text,
        and return it as a single string. Result is cached for the server session.
        """
        if self._cached_text is not None:
            return self._cached_text

        if not settings.fund2_drive_folder_id:
            logger.warning("FUND2_DRIVE_FOLDER_ID is not set — LP chat has no documents")
            return None

        try:
            drive = self._drive()
            results = drive.files().list(
                q=(
                    f"'{settings.fund2_drive_folder_id}' in parents"
                    " and mimeType='application/pdf'"
                    " and trashed=false"
                ),
                fields="files(id, name)",
                orderBy="name",
            ).execute()
        except Exception as e:
            logger.error("Failed to list Drive folder", error=str(e))
            return None

        files = results.get("files", [])
        if not files:
            logger.warning("No PDF files found in Drive folder", folder_id=settings.fund2_drive_folder_id)
            return None

        texts = []
        for file in files:
            try:
                request = drive.files().get_media(fileId=file["id"])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()

                fh.seek(0)
                with pdfplumber.open(fh) as pdf:
                    page_texts = [p.extract_text() for p in pdf.pages if p.extract_text()]

                if page_texts:
                    texts.append(f"=== {file['name']} ===\n" + "\n".join(page_texts))
                    logger.info("Loaded PDF from Drive", file=file["name"], pages=len(page_texts))
            except Exception as e:
                logger.error("Failed to load PDF", file=file["name"], error=str(e))

        if not texts:
            return None

        self._cached_text = "\n\n".join(texts)
        logger.info("PDF context ready", files=len(texts), chars=len(self._cached_text))
        return self._cached_text


pdf_service = PDFService()
