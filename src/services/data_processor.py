"""
Data processor service for manipulating and analyzing fund data.
"""

import pandas as pd
from typing import Any, Dict, Optional

from src.models.query import QueryIntent, QueryType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Processes fund and portfolio data based on query intent."""

    def _filter_rv_portfolio(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter portfolio to only show RV portfolio companies.

        Args:
            df: Portfolio DataFrame

        Returns:
            Filtered DataFrame with only RV portfolio companies
        """
        if df.empty:
            return df

        # Find the "Is RV portfolio?" column
        rv_col = self._find_column(df, "Is RV portfolio")

        if rv_col:
            # Filter to only "Yes" values
            df = df[df[rv_col].astype(str).str.lower().isin(['yes', 'y', 'true', '1'])]
            logger.debug("Filtered to RV portfolio only", count=len(df))

        return df

    def process_fund_metric(self, df: pd.DataFrame, metric: str, time_period: str = "latest") -> Dict[str, Any]:
        """
        Extract a specific fund metric.

        Args:
            df: Fund metrics DataFrame
            metric: Metric name (TVPI, DPI, IRR, etc.)
            time_period: Time period to get (latest, Q1 2024, etc.)

        Returns:
            Dictionary with metric data
        """
        try:
            if df.empty:
                return {"error": "No fund metrics data available"}

            # Find the metric column (flexible matching)
            metric_col = None
            metric_lower = metric.lower()

            # Try different matching strategies
            for col in df.columns:
                col_lower = col.lower()

                # Strategy 1: Exact match
                if col_lower == metric_lower:
                    metric_col = col
                    break

                # Strategy 2: Match with "RV " prefix (e.g., "TVPI" matches "RV TVPI")
                if col_lower == f"rv {metric_lower}":
                    metric_col = col
                    break

                # Strategy 3: Column ends with metric (e.g., "TVPI" matches "RV TVPI")
                if col_lower.endswith(metric_lower):
                    metric_col = col
                    break

                # Strategy 4: Metric is in column name
                if metric_lower in col_lower:
                    metric_col = col
                    break

            if not metric_col:
                return {"error": f"Metric '{metric}' not found in data. Available columns: {', '.join(df.columns)}"}

            # Get latest or specific period
            if time_period == "latest":
                # Assume last row is most recent
                value = df[metric_col].iloc[-1]
                period = df.iloc[-1].get(df.columns[0], "Latest")  # First column usually has period
            else:
                # Try to find specific period
                period_col = df.columns[0]  # Assume first column is period
                matching_rows = df[df[period_col].str.contains(time_period, case=False, na=False)]
                if not matching_rows.empty:
                    value = matching_rows[metric_col].iloc[-1]
                    period = matching_rows[period_col].iloc[-1]
                else:
                    value = df[metric_col].iloc[-1]
                    period = "Latest"

            logger.info("Processed fund metric", metric=metric, value=value, period=period)

            return {
                "metric": metric,
                "value": value,
                "period": period,
            }

        except Exception as e:
            logger.error("Error processing fund metric", error=str(e), metric=metric)
            return {"error": str(e)}

    def _find_column(self, df: pd.DataFrame, search_term: str) -> str:
        """
        Flexibly find a column in the dataframe matching the search term.

        Args:
            df: DataFrame to search
            search_term: Term to search for

        Returns:
            Column name or None
        """
        search_lower = search_term.lower().replace("_", " ").strip()

        # Strategy 1: Exact match
        for col in df.columns:
            if col.lower().replace("_", " ").strip() == search_lower:
                return col

        # Strategy 2: Column ends with search term
        for col in df.columns:
            if col.lower().strip().endswith(search_lower):
                return col

        # Strategy 3: Search term is in column
        for col in df.columns:
            if search_lower in col.lower():
                return col

        # Strategy 4: Handle common aliases
        aliases = {
            "return": ["return", "investment return", "investment (w/o fees) return"],
            "investment": ["rv investment", "investment", "rv investment, $k"],
            "valuation": ["valuation", "post valuation", "post-money valuation"],
            "company": ["company name", "name"],
            "stage": ["stage", "investment stage", "round stage"],
        }

        for alias, variations in aliases.items():
            if alias in search_lower:
                for variation in variations:
                    for col in df.columns:
                        if variation in col.lower():
                            return col

        return None

    def _select_key_columns(self, df: pd.DataFrame, show_all: bool = False) -> pd.DataFrame:
        """
        Select only key columns for display unless show_all is True.

        Args:
            df: Portfolio DataFrame
            show_all: If True, return all columns; if False, return only key columns

        Returns:
            DataFrame with selected columns
        """
        if show_all or df.empty:
            return df

        # Define key columns to show by default
        key_column_keywords = [
            'company name',
            'vertical',
            'rv investment',
            'investment return',
            'last round post-money valuation',
            'founded',
            'hq',
        ]

        # Find actual column names that match keywords
        selected_cols = []
        for keyword in key_column_keywords:
            col = self._find_column(df, keyword)
            if col and col not in selected_cols:
                selected_cols.append(col)

        # If we found key columns, use them; otherwise return all
        if selected_cols:
            # Always include company name first if it exists
            company_col = self._find_column(df, 'company name')
            if company_col and company_col in selected_cols:
                selected_cols.remove(company_col)
                selected_cols.insert(0, company_col)

            return df[selected_cols]

        return df

    def process_portfolio_ranking(
        self, df: pd.DataFrame, sort_by: str, limit: int = 5, show_all_details: bool = False, ascending: bool = False
    ) -> pd.DataFrame:
        """
        Rank portfolio companies by a criterion.

        Args:
            df: Portfolio DataFrame
            sort_by: Column to sort by
            limit: Number of results to return
            show_all_details: Whether to show all columns or just key ones
            ascending: Sort ascending (True for worst/lowest, False for top/best)

        Returns:
            Filtered and sorted DataFrame
        """
        try:
            if df.empty:
                return df

            # Filter to RV portfolio only
            df = self._filter_rv_portfolio(df)

            # Make a copy to avoid modifying original
            df = df.copy()

            # Find the sort column using flexible matching
            sort_col = self._find_column(df, sort_by)

            if not sort_col:
                logger.warning("Sort column not found", sort_by=sort_by, available=list(df.columns))
                # Return first N rows
                return df.head(limit)

            logger.debug(f"Sorting by column: '{sort_col}' for search term: '{sort_by}', ascending={ascending}")

            # Clean and convert to numeric
            # Remove common formatting characters: $, K, M, commas, spaces
            df[sort_col] = (
                df[sort_col]
                .astype(str)
                .str.replace('$', '', regex=False)
                .str.replace('K', '', regex=False)
                .str.replace('M', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.strip()
            )

            # Convert to numeric
            df[sort_col] = pd.to_numeric(df[sort_col], errors='coerce')

            # Drop rows where conversion failed (NaN)
            df = df.dropna(subset=[sort_col])

            # Sort and take top N - RESET INDEX to preserve order!
            result = (
                df.sort_values(by=sort_col, ascending=ascending)
                .head(limit)
                .reset_index(drop=True)
            )

            # Select key columns unless user wants all details
            result = self._select_key_columns(result, show_all=show_all_details)

            logger.info(
                "Processed portfolio ranking",
                sort_by=sort_col,
                ascending=ascending,
                count=len(result),
                show_all=show_all_details,
                top_values=result[sort_col].tolist() if sort_col in result.columns and not result.empty else []
            )

            return result

        except Exception as e:
            logger.error("Error processing portfolio ranking", error=str(e), exc_info=True)
            return df.head(limit)

    def process_portfolio_list(self, df: pd.DataFrame, filters: Dict[str, Any], show_all_details: bool = False) -> pd.DataFrame:
        """
        Filter portfolio companies based on criteria.

        Args:
            df: Portfolio DataFrame
            filters: Dictionary of filters to apply

        Returns:
            Filtered DataFrame
        """
        try:
            if df.empty:
                return df

            # Filter to RV portfolio only
            result = self._filter_rv_portfolio(df.copy())

            # Apply each filter
            for key, value in filters.items():
                # Find matching column using flexible matching
                filter_col = self._find_column(result, key)

                if filter_col:
                    # Apply filter (case-insensitive string contains)
                    result = result[
                        result[filter_col].astype(str).str.contains(str(value), case=False, na=False)
                    ]
                else:
                    logger.warning("Filter column not found", key=key, available=list(result.columns))

            # Select key columns unless user wants all details
            result = self._select_key_columns(result, show_all=show_all_details)

            logger.info("Processed portfolio list", filters=filters, count=len(result), show_all=show_all_details)

            return result

        except Exception as e:
            logger.error("Error processing portfolio list", error=str(e))
            return df

    def process_query(self, intent: QueryIntent, fund_df: pd.DataFrame, portfolio_df: pd.DataFrame) -> Any:
        """
        Process a query based on its intent.

        Args:
            intent: Parsed query intent
            fund_df: Fund metrics DataFrame
            portfolio_df: Portfolio DataFrame

        Returns:
            Processed data
        """
        if intent.query_type == QueryType.GENERAL_CHAT:
            # For general chat, return None (will be handled by OpenAI directly)
            return None

        if intent.query_type == QueryType.FUND_METRIC:
            if not intent.metric:
                return {"error": "No metric specified"}
            return self.process_fund_metric(fund_df, intent.metric, intent.time_period or "latest")

        elif intent.query_type == QueryType.PORTFOLIO_RANKING:
            sort_by = intent.sort_by or "investment_amount"
            limit = intent.limit or 5
            return self.process_portfolio_ranking(
                portfolio_df, sort_by, limit, show_all_details=intent.show_all_details, ascending=intent.ascending
            )

        elif intent.query_type == QueryType.PORTFOLIO_LIST:
            return self.process_portfolio_list(
                portfolio_df, intent.filters, show_all_details=intent.show_all_details
            )

        elif intent.query_type == QueryType.COMPANY_DETAIL:
            if intent.company_name:
                filters = {"company_name": intent.company_name}
                # For specific company details, show all columns by default
                return self.process_portfolio_list(
                    portfolio_df, filters, show_all_details=True
                )
            return {"error": "No company name specified"}

        else:
            return {"error": "Unknown query type"}


# Global data processor instance
data_processor = DataProcessor()
