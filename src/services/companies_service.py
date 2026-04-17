"""
In-memory company search service backed by a static CSV export from Affinity.
Loads from Google Drive when AFFINITY_DRIVE_FILE_ID is set, falls back to local file.
"""

import io
import os

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Columns to show in the frontend table
DISPLAY_COLUMNS = [
    "Name",
    "Description",
    "Industry",
    "Location (Country)",
    "Investment Stage",
    "Year Founded",
    "Number of Employees",
    "Investors",
    "Last Funding Amount (USD)",
    "Last Funding Date",
    "Total Funding Amount (USD)",
    "People",
    "Last Contact",
]

# Columns searched by the text query
SEARCH_COLUMNS = ["Name", "Description", "Industry", "Investors", "People"]


class CompaniesService:
    """Loads Affinity CSV once and provides fast in-memory search."""

    def __init__(self):
        self.df: pd.DataFrame = pd.DataFrame()
        self.links: dict[str, str] = {}      # Name → Website URL
        self.linkedin: dict[str, str] = {}    # Name → LinkedIn URL
        self.filters: dict[str, list[str]] = {}
        self._load()

    def _load(self):
        if settings.affinity_drive_file_id:
            try:
                credentials = Credentials.from_service_account_file(
                    settings.google_credentials_file,
                    scopes=["https://www.googleapis.com/auth/drive.readonly"],
                )
                drive = build("drive", "v3", credentials=credentials, cache_discovery=False)
                request = drive.files().get_media(fileId=settings.affinity_drive_file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)
                df = pd.read_csv(fh, encoding="utf-8-sig", low_memory=False)
                logger.info("Loaded Affinity CSV from Google Drive", rows=len(df), columns=len(df.columns))
            except Exception as e:
                logger.error("Failed to load Affinity CSV from Google Drive", error=str(e))
                return
        else:
            csv_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "affinity.csv"))
            if not os.path.exists(csv_path):
                logger.warning("Affinity CSV not found", path=csv_path)
                return
            df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
            logger.info("Loaded Affinity CSV from local file", rows=len(df), columns=len(df.columns))

        # --- Pre-filters ---
        # Keep only high / mid level of connection
        loc_col = next((c for c in df.columns if "level of connection" in c.lower()), None)
        if loc_col:
            df = df[df[loc_col].astype(str).str.strip().str.lower().isin(["high", "mid"])]
            df = df.drop(columns=[loc_col])

        # Drop rows where Last Contact is blank
        if "Last Contact" in df.columns:
            df = df[df["Last Contact"].astype(str).str.strip().ne("").ne("nan") & df["Last Contact"].notna()]

        # Drop companies located in Russia
        if "Location (Country)" in df.columns:
            df = df[df["Location (Country)"].astype(str).str.strip().str.lower() != "russia"]

        logger.info("After pre-filters", rows=len(df))

        # --- Extract links ---
        if "Website" in df.columns:
            for _, row in df.iterrows():
                url = str(row["Website"]).strip()
                name = str(row["Name"]).strip()
                if url and name and url.startswith("http"):
                    self.links[name] = url

        # Extract LinkedIn URLs
        li_col = next((c for c in df.columns if c == "LinkedIn URL"), None)
        if li_col:
            for _, row in df.iterrows():
                url = str(row[li_col]).strip()
                name = str(row["Name"]).strip()
                if url and name and url.startswith("http"):
                    self.linkedin[name] = url

        # --- Keep only display columns (use first occurrence for duplicates) ---
        keep = []
        seen = set()
        for col in df.columns:
            if col in DISPLAY_COLUMNS and col not in seen:
                keep.append(col)
                seen.add(col)

        df = df[keep].copy()

        # --- Format numeric columns before converting to str ---
        for col in ["Year Founded", "Number of Employees"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").apply(
                    lambda x: str(int(x)) if pd.notna(x) else ""
                )

        for col in ["Last Funding Amount (USD)", "Total Funding Amount (USD)"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").apply(
                    lambda x: f"{int(x):,}" if pd.notna(x) else ""
                )

        df = df.fillna("").astype(str)

        # --- Drop rows with no description ---
        if "Description" in df.columns:
            blank = {"", "nan", "none", "n/a", "na", "-"}
            df = df[~df["Description"].str.strip().str.lower().isin(blank)]

        df = df.reset_index(drop=True)
        self.df = df

        # --- Build filter options ---
        # Count companies per industry, keep only those with >= 5
        if "Industry" in df.columns:
            industry_counts: dict[str, int] = {}
            for val in df["Industry"]:
                for part in str(val).split(";"):
                    part = part.strip()
                    if part:
                        industry_counts[part] = industry_counts.get(part, 0) + 1
            industries_list = sorted(k for k, v in industry_counts.items() if v >= 20)
        else:
            industries_list = []

        self.filters = {
            "industries": industries_list,
            "countries": sorted(df["Location (Country)"].unique().tolist()) if "Location (Country)" in df.columns else [],
            "stages": sorted(df["Investment Stage"].unique().tolist()) if "Investment Stage" in df.columns else [],
        }
        # Remove empty strings from filter options
        for key in self.filters:
            self.filters[key] = [v for v in self.filters[key] if v.strip()]

        logger.info(
            "Companies service ready",
            companies=len(self.df),
            links=len(self.links),
            linkedin=len(self.linkedin),
        )

    def search(
        self,
        query: str = "",
        industry: str = "",
        country: str = "",
        stage: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """Search and filter companies, returning up to `limit` rows starting at `offset`."""
        df = self.df

        # Text search — name matches first, then other column matches
        if query:
            q = query.lower()
            name_mask = df["Name"].str.lower().str.contains(q, na=False) if "Name" in df.columns else pd.Series(False, index=df.index)
            other_mask = pd.Series(False, index=df.index)
            for col in SEARCH_COLUMNS:
                if col in df.columns and col != "Name":
                    other_mask = other_mask | df[col].str.lower().str.contains(q, na=False)
            df = pd.concat([df[name_mask], df[other_mask & ~name_mask]])

        # Dropdown filters (industry uses contains since values are semicolon-separated)
        if industry and "Industry" in df.columns:
            df = df[df["Industry"].str.contains(industry, case=False, na=False)]
        if country and "Location (Country)" in df.columns:
            df = df[df["Location (Country)"] == country]
        if stage and "Investment Stage" in df.columns:
            df = df[df["Investment Stage"] == stage]

        total = len(df)
        df = df.iloc[offset:offset + limit]

        return {
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records"),
            "links": self.links,
            "linkedin": self.linkedin,
            "total": total,
            "filters": self.filters,
        }


# Global instance — loaded once at import time
companies_service = CompaniesService()
