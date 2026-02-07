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
            # Define the required scopes
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
            ]

            # Load credentials from file
            credentials = Credentials.from_service_account_file(
                settings.google_credentials_file, scopes=scopes
            )

            # Initialize gspread client
            self.client = gspread.authorize(credentials)

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

    def clear_cache(self):
        """Clear all cached sheet data."""
        if hasattr(self.get_fund_metrics, 'clear_cache'):
            self.get_fund_metrics.clear_cache()
        if hasattr(self.get_portfolio_data, 'clear_cache'):
            self.get_portfolio_data.clear_cache()
        logger.info("Cleared sheets cache")


# Global sheets service instance
sheets_service = SheetsService()
