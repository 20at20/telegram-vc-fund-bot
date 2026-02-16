"""
In-memory company search service backed by a static CSV export from Affinity.
"""

import os
import pandas as pd
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
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "affinity.csv")
        csv_path = os.path.normpath(csv_path)

        if not os.path.exists(csv_path):
            logger.warning("Affinity CSV not found", path=csv_path)
            return

        df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
        logger.info("Loaded raw CSV", rows=len(df), columns=len(df.columns))

        # --- Pre-filters ---
        # Keep only high / mid level of connection
        loc_col = next((c for c in df.columns if "level of connection" in c.lower()), None)
        if loc_col:
            df = df[df[loc_col].astype(str).str.strip().str.lower().isin(["high", "mid"])]
            df = df.drop(columns=[loc_col])

        # Drop rows where Last Contact is blank
        if "Last Contact" in df.columns:
            df = df[df["Last Contact"].astype(str).str.strip().ne("").ne("nan") & df["Last Contact"].notna()]

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
        df = df.fillna("").astype(str)
        df = df.reset_index(drop=True)
        self.df = df

        # --- Build filter options ---
        # Split semicolon-separated industries into unique individual values
        if "Industry" in df.columns:
            all_industries = set()
            for val in df["Industry"].unique():
                for part in str(val).split(";"):
                    part = part.strip()
                    if part:
                        all_industries.add(part)
            industries_list = sorted(all_industries)
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

        # Text search across key columns
        if query:
            q = query.lower()
            mask = pd.Series(False, index=df.index)
            for col in SEARCH_COLUMNS:
                if col in df.columns:
                    mask = mask | df[col].str.lower().str.contains(q, na=False)
            df = df[mask]

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
