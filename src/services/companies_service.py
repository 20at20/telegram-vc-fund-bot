"""
Company search service backed by Affinity CSV stored in Google Drive.
"""

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_COLUMNS = ["Name", "Description", "Industry", "Investors", "People"]


class CompaniesService:
    async def search(
        self,
        query: str = "",
        industry: str = "",
        country: str = "",
        stage: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        from src.services.sheets_service import sheets_service

        df, links, linkedin, filters = await sheets_service.get_companies_data()

        if df.empty:
            return {
                "columns": [],
                "rows": [],
                "links": {},
                "linkedin": {},
                "total": 0,
                "filters": filters,
            }

        # Text search across key columns
        if query:
            q = query.lower()
            mask = pd.Series(False, index=df.index)
            for col in SEARCH_COLUMNS:
                if col in df.columns:
                    mask = mask | df[col].str.lower().str.contains(q, na=False)
            df = df[mask]

        # Dropdown filters
        if industry and "Industry" in df.columns:
            df = df[df["Industry"].str.contains(industry, case=False, na=False)]
        if country and "Location (Country)" in df.columns:
            df = df[df["Location (Country)"] == country]
        if stage and "Investment Stage" in df.columns:
            df = df[df["Investment Stage"] == stage]

        total = len(df)
        df = df.iloc[offset : offset + limit]

        return {
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records"),
            "links": links,
            "linkedin": linkedin,
            "total": total,
            "filters": filters,
        }


companies_service = CompaniesService()
