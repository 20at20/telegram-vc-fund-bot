"""
One-time script: download PDFs from the Fund II Drive folder, extract their text,
and upload lightweight .txt files back to the same folder.

The server loads .txt files on startup — much faster than parsing raw PDFs with pdfplumber.
Re-run this script any time the source PDFs change.

Requirements:
- The service account must have Editor (not just Viewer) access to the Drive folder.
  Go to Drive → right-click folder → Share → change the service account from Viewer to Editor.

Usage:
    FUND2_DRIVE_FOLDER_ID=<folder_id> python scripts/compile_lp_docs.py

Optional env vars:
    GOOGLE_CREDENTIALS_FILE  — path to service account JSON (default: config/credentials/google_service_account.json)
    LOCAL_OUTPUT_DIR         — if set, also save .txt files locally to this directory
"""

import io
import os
import re
import sys

import pdfplumber
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDS_FILE = os.environ.get(
    "GOOGLE_CREDENTIALS_FILE", "config/credentials/google_service_account.json"
)
FOLDER_ID = os.environ.get("FUND2_DRIVE_FOLDER_ID", "")

if not FOLDER_ID:
    print("ERROR: FUND2_DRIVE_FOLDER_ID env var is not set.")
    sys.exit(1)


def clean_text(text: str) -> str:
    """Remove common PDF noise: page numbers, repeated blank lines."""
    # Remove standalone page numbers (e.g. "1", "12", "Page 3 of 10")
    text = re.sub(r"(?m)^\s*(Page\s+)?\d+(\s+of\s+\d+)?\s*$", "", text)
    # Collapse 3+ blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    # List PDFs in the folder
    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false",
        fields="files(id, name)",
        orderBy="name",
    ).execute()
    files = results.get("files", [])

    if not files:
        print("No PDF files found in the Drive folder.")
        return

    print(f"Found {len(files)} PDF(s) to compile.")

    for f in files:
        print(f"\nProcessing: {f['name']} ...", end=" ", flush=True)

        # Download PDF
        req = drive.files().get_media(fileId=f["id"])
        fh = io.BytesIO()
        dl = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = dl.next_chunk()
        fh.seek(0)

        # Extract and clean text
        with pdfplumber.open(fh) as pdf:
            pages = [p.extract_text() for p in pdf.pages if p.extract_text()]

        if not pages:
            print("SKIPPED (no extractable text)")
            continue

        raw_text = "\n\n".join(pages)
        cleaned = clean_text(raw_text)
        content = f"=== {f['name']} ===\n\n{cleaned}"
        txt_bytes = content.encode("utf-8")

        txt_name = re.sub(r"\.pdf$", ".txt", f["name"], flags=re.IGNORECASE)

        # Optionally save locally
        local_dir = os.environ.get("LOCAL_OUTPUT_DIR", "")
        if local_dir:
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, txt_name)
            with open(local_path, "wb") as out:
                out.write(txt_bytes)
            print(f"saved locally → {local_path}", end=" | ", flush=True)

        # Upload to Drive
        media = MediaIoBaseUpload(io.BytesIO(txt_bytes), mimetype="text/plain", resumable=False)
        existing = drive.files().list(
            q=f"'{FOLDER_ID}' in parents and name='{txt_name}' and trashed=false",
            fields="files(id)",
        ).execute().get("files", [])

        if existing:
            drive.files().update(fileId=existing[0]["id"], media_body=media).execute()
            print(f"Drive updated → {txt_name} ({len(txt_bytes):,} bytes)")
        else:
            drive.files().create(
                body={"name": txt_name, "parents": [FOLDER_ID]},
                media_body=media,
            ).execute()
            print(f"Drive created → {txt_name} ({len(txt_bytes):,} bytes)")

    print("\nDone. All PDFs compiled to .txt and uploaded to Drive.")


if __name__ == "__main__":
    main()
