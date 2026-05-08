"""
Google Sheets service for fetching fund and portfolio data.
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from src.utils.cache import cache_with_ttl
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SheetsService:
    """Service for accessing Google Sheets data."""

    def __init__(self):
        """Initialize Google Sheets service."""
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize gspread client with service account credentials."""
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
            ]

            self.credentials = Credentials.from_service_account_file(
                settings.google_credentials_file, scopes=scopes
            )
            self.client = gspread.authorize(self.credentials)

            logger.info("Google Sheets client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Google Sheets client", error=str(e))
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _fetch_sheet_data(self, sheet_id: str, range_name: str) -> list:
        """
        Fetch data from a Google Sheet.

        Args:
            sheet_id: Google Sheet ID
            range_name: Sheet range (e.g., "Sheet1!A1:Z100")

        Returns:
            List of rows from the sheet
        """
        try:
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(sheet_id)

            # Parse range to get sheet name and cell range
            if "!" in range_name:
                sheet_name, cell_range = range_name.split("!", 1)
            else:
                sheet_name = range_name
                cell_range = None

            # Get the worksheet
            worksheet = spreadsheet.worksheet(sheet_name)

            # Fetch data
            if cell_range:
                data = worksheet.get(cell_range)
            else:
                data = worksheet.get_all_values()

            logger.debug(
                "Fetched sheet data",
                sheet_id=sheet_id,
                range=range_name,
                rows=len(data),
            )

            return data

        except Exception as e:
            logger.error(
                "Error fetching sheet data",
                sheet_id=sheet_id,
                range=range_name,
                error=str(e),
            )
            raise

    def _clean_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows where all values are empty or NaN.
        IMPORTANT: Stops at first blank cell in first column (Time/Period) to avoid
        reading summary tables that come after main data.

        Args:
            df: DataFrame to clean

        Returns:
            DataFrame with empty rows removed, stopping at first blank in first column
        """
        if df.empty:
            return df

        # First, find where the first column (Time/Period) becomes blank
        # This marks the boundary between main data and summary tables
        first_col = df.columns[0]

        # Find the first row where the first column is empty/blank
        first_blank_idx = None
        for idx, value in df[first_col].items():
            # Check if value is NaN, None, empty string, or whitespace-only
            if pd.isna(value) or str(value).strip() == '':
                first_blank_idx = idx
                break

        # If we found a blank, cut off everything from that point
        if first_blank_idx is not None:
            df = df.iloc[:first_blank_idx].copy()
            logger.debug(f"Stopped reading at row {first_blank_idx} (first blank in '{first_col}' column)")

        # Now remove any completely empty rows within the remaining data
        df_cleaned = df.dropna(how='all')

        # Also remove rows where all values are empty strings
        df_cleaned = df_cleaned[~df_cleaned.apply(lambda row: row.astype(str).str.strip().eq('').all(), axis=1)]

        return df_cleaned.reset_index(drop=True)

    @cache_with_ttl(ttl=300)  # 5-minute cache
    async def get_fund_metrics(self) -> pd.DataFrame:
        """
        Fetch fund performance metrics from Google Sheets.
        Automatically removes empty rows.

        Returns:
            DataFrame with fund metrics
        """
        try:
            data = await self._fetch_sheet_data(
                settings.fund_metrics_sheet_id, settings.fund_metrics_range
            )

            if not data:
                logger.warning("No fund metrics data found")
                return pd.DataFrame()

            # Convert to DataFrame (first row as headers)
            df = pd.DataFrame(data[1:], columns=data[0])

            # Remove empty rows
            df = self._clean_empty_rows(df)

            logger.info("Loaded fund metrics", rows=len(df))
            return df

        except Exception as e:
            logger.error("Error loading fund metrics", error=str(e))
            raise

    @cache_with_ttl(ttl=300)  # 5-minute cache
    async def get_portfolio_data(self) -> pd.DataFrame:
        """
        Fetch portfolio company data from Google Sheets.
        Automatically removes empty rows.

        Returns:
            DataFrame with portfolio data
        """
        try:
            data = await self._fetch_sheet_data(
                settings.portfolio_sheet_id, settings.portfolio_range
            )

            if not data:
                logger.warning("No portfolio data found")
                return pd.DataFrame()

            # Convert to DataFrame (first row as headers)
            df = pd.DataFrame(data[1:], columns=data[0])

            # Remove empty rows
            df = self._clean_empty_rows(df)

            logger.info("Loaded portfolio data", rows=len(df))
            return df

        except Exception as e:
            logger.error("Error loading portfolio data", error=str(e))
            raise

    @cache_with_ttl(ttl=300)  # 5-minute cache
    async def get_deals_data(self) -> tuple:
        """
        Fetch deals pipeline data from Google Sheets.

        Returns:
            Tuple of (DataFrame with deals data, dict of company name -> URL)
        """
        try:
            if not settings.deals_sheet_id:
                logger.warning("No deals sheet ID configured")
                return pd.DataFrame(), {}

            data = await self._fetch_sheet_data(
                settings.deals_sheet_id, settings.deals_range
            )

            if not data:
                logger.warning("No deals data found")
                return pd.DataFrame(), {}

            # Convert to DataFrame (first row as headers)
            df = pd.DataFrame(data[1:], columns=data[0])

            # Remove empty rows
            df = self._clean_empty_rows(df)

            # Extract links from the "Link" column into a dict, then drop it from the DataFrame
            links = {}
            link_col = next((c for c in df.columns if c.lower() == 'link'), None)
            company_col = next((c for c in df.columns if 'company' in c.lower()), None)
            if link_col and company_col:
                for _, row in df.iterrows():
                    url = str(row[link_col]).strip()
                    name = str(row[company_col]).strip()
                    if url and name and url.startswith('http'):
                        links[name] = url
                df = df.drop(columns=[link_col])

            logger.info("Loaded deals data", rows=len(df), links=len(links))
            return df, links

        except Exception as e:
            logger.error("Error loading deals data", error=str(e))
            raise

    @cache_with_ttl(ttl=300)  # 5-minute cache
    async def get_experts_data(self) -> tuple:
        """
        Fetch experts directory data from Google Sheets.

        Returns:
            Tuple of (DataFrame with experts data, dict of name -> LinkedIn URL)
        """
        try:
            if not settings.experts_sheet_id:
                logger.warning("No experts sheet ID configured")
                return pd.DataFrame(), {}

            data = await self._fetch_sheet_data(
                settings.experts_sheet_id, settings.experts_range
            )

            if not data:
                logger.warning("No experts data found")
                return pd.DataFrame(), {}

            df = pd.DataFrame(data[1:], columns=data[0])
            df = self._clean_empty_rows(df)

            # Extract LinkedIn URLs into a dict, then drop the column
            links = {}
            link_col = next((c for c in df.columns if 'linkedin' in c.lower()), None)
            name_col = next((c for c in df.columns if 'name' in c.lower()), None)
            if link_col and name_col:
                for _, row in df.iterrows():
                    url = str(row[link_col]).strip()
                    name = str(row[name_col]).strip()
                    if url and name and url.startswith('http'):
                        links[name] = url
                df = df.drop(columns=[link_col])

            logger.info("Loaded experts data", rows=len(df), links=len(links))
            return df, links

        except Exception as e:
            logger.error("Error loading experts data", error=str(e))
            raise

    @cache_with_ttl(ttl=300)  # 5-minute cache
    async def get_asks_data(self) -> tuple:
        """
        Fetch portfolio asks data from Google Sheets.

        Returns:
            Tuple of (DataFrame with asks data, dict of company name -> URL)
        """
        try:
            if not settings.asks_sheet_id:
                logger.warning("No asks sheet ID configured")
                return pd.DataFrame(), {}

            data = await self._fetch_sheet_data(
                settings.asks_sheet_id, settings.asks_range
            )

            if not data:
                logger.warning("No asks data found")
                return pd.DataFrame(), {}

            df = pd.DataFrame(data[1:], columns=data[0])
            df = self._clean_empty_rows(df)

            # Extract links from the "Link" column into a dict, then drop it
            links = {}
            link_col = next((c for c in df.columns if c.lower() == 'link'), None)
            company_col = next((c for c in df.columns if 'company' in c.lower()), None)
            if link_col and company_col:
                for _, row in df.iterrows():
                    url = str(row[link_col]).strip()
                    name = str(row[company_col]).strip()
                    if url and name and url.startswith('http'):
                        links[name] = url
                df = df.drop(columns=[link_col])

            logger.info("Loaded asks data", rows=len(df), links=len(links))
            return df, links

        except Exception as e:
            logger.error("Error loading asks data", error=str(e))
            raise

    @cache_with_ttl(ttl=1800)  # 30-minute cache — Affinity CSV is uploaded manually
    async def get_companies_data(self) -> tuple:
        """
        Download the latest Affinity CSV from Google Drive and return processed data.

        Returns:
            Tuple of (df, links, linkedin, filters)
        """
        import io
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        try:
            if not settings.affinity_drive_folder_id:
                logger.warning("No Affinity Drive folder ID configured")
                return pd.DataFrame(), {}, {}, {}

            drive = build("drive", "v3", credentials=self.credentials)

            results = drive.files().list(
                q=f"'{settings.affinity_drive_folder_id}' in parents and mimeType='text/csv' and trashed=false",
                orderBy="modifiedTime desc",
                pageSize=1,
                fields="files(id, name)",
            ).execute()

            files = results.get("files", [])
            if not files:
                logger.warning("No CSV files found in Affinity Drive folder")
                return pd.DataFrame(), {}, {}, {}

            file_id = files[0]["id"]
            logger.info("Downloading Affinity CSV from Drive", file_name=files[0]["name"])

            request = drive.files().get_media(fileId=file_id)
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            buffer.seek(0)
            df = pd.read_csv(buffer, encoding="utf-8-sig", low_memory=False)
            logger.info("Loaded raw Affinity CSV", rows=len(df), columns=len(df.columns))

            # Filter to high/mid connections only
            loc_col = next((c for c in df.columns if "level of connection" in c.lower()), None)
            if loc_col:
                df = df[df[loc_col].astype(str).str.strip().str.lower().isin(["high", "mid"])]
                df = df.drop(columns=[loc_col])

            # Drop rows with no Last Contact date
            if "Last Contact" in df.columns:
                df = df[
                    df["Last Contact"].astype(str).str.strip().ne("").ne("nan")
                    & df["Last Contact"].notna()
                ]

            logger.info("After pre-filters", rows=len(df))

            # Extract Website and LinkedIn URLs before dropping columns
            links = {}
            if "Website" in df.columns:
                for _, row in df.iterrows():
                    url = str(row["Website"]).strip()
                    name = str(row["Name"]).strip()
                    if url and name and url.startswith("http"):
                        links[name] = url

            linkedin = {}
            li_col = next((c for c in df.columns if c == "LinkedIn URL"), None)
            if li_col:
                for _, row in df.iterrows():
                    url = str(row[li_col]).strip()
                    name = str(row["Name"]).strip()
                    if url and name and url.startswith("http"):
                        linkedin[name] = url

            # Keep only display columns
            display_columns = [
                "Name", "Description", "Industry", "Location (Country)",
                "Investment Stage", "Year Founded", "Number of Employees",
                "Investors", "Last Funding Amount (USD)", "Last Funding Date",
                "Total Funding Amount (USD)", "People", "Last Contact",
            ]
            keep, seen = [], set()
            for col in df.columns:
                if col in display_columns and col not in seen:
                    keep.append(col)
                    seen.add(col)

            df = df[keep].copy().fillna("").astype(str).reset_index(drop=True)

            # Build dropdown filter options
            filters: dict = {"industries": [], "countries": [], "stages": []}
            if "Industry" in df.columns:
                all_industries: set = set()
                for val in df["Industry"].unique():
                    for part in str(val).split(";"):
                        part = part.strip()
                        if part:
                            all_industries.add(part)
                filters["industries"] = sorted(all_industries)
            if "Location (Country)" in df.columns:
                filters["countries"] = sorted(v for v in df["Location (Country)"].unique() if v.strip())
            if "Investment Stage" in df.columns:
                filters["stages"] = sorted(v for v in df["Investment Stage"].unique() if v.strip())

            logger.info("Companies data ready", companies=len(df), links=len(links), linkedin=len(linkedin))
            return df, links, linkedin, filters

        except Exception as e:
            logger.error("Error loading companies data from Drive", error=str(e))
            raise

    def clear_cache(self):
        """Clear all cached sheet data."""
        if hasattr(self.get_fund_metrics, 'clear_cache'):
            self.get_fund_metrics.clear_cache()
        if hasattr(self.get_portfolio_data, 'clear_cache'):
            self.get_portfolio_data.clear_cache()
        if hasattr(self.get_deals_data, 'clear_cache'):
            self.get_deals_data.clear_cache()
        if hasattr(self.get_experts_data, 'clear_cache'):
            self.get_experts_data.clear_cache()
        if hasattr(self.get_asks_data, 'clear_cache'):
            self.get_asks_data.clear_cache()
        if hasattr(self.get_companies_data, 'clear_cache'):
            self.get_companies_data.clear_cache()
        logger.info("Cleared sheets cache")


# Global sheets service instance
sheets_service = SheetsService()
