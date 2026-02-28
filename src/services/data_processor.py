"""
Data processor service for manipulating and analyzing fund data.
"""

import pandas as pd
from typing import Any, Dict, Optional

from src.models.query import QueryIntent, QueryType
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Columns to hide from all query results (internal/irrelevant data)
HIDDEN_COLUMNS = [
    "Co-investment, $K",
    "Co-investment investment value, $K",
    "Co-investment fees, $K",
]


# Industry vertical synonyms mapping - helps match user queries to actual sheet values
# E.g., "finance" or "financial industry" should match "fintech"
VERTICAL_SYNONYMS = {
    "fintech": ["fintech", "financial", "finance", "banking", "financial services", "fin-tech", "payments"],
    "healthtech": ["healthtech", "health", "healthcare", "medical", "digital health", "health tech", "medtech"],
    "ai": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "generative ai"],
    "saas": ["saas", "software as a service", "cloud software", "enterprise software", "b2b software"],
    "ecommerce": ["ecommerce", "e-commerce", "retail", "online retail", "commerce", "marketplace"],
    "edtech": ["edtech", "education", "ed-tech", "learning", "educational technology", "e-learning"],
    "proptech": ["proptech", "real estate", "property", "prop-tech", "real-estate"],
    "insurtech": ["insurtech", "insurance", "insur-tech"],
    "crypto": ["crypto", "blockchain", "web3", "cryptocurrency", "defi", "digital assets"],
    "mobility": ["mobility", "transportation", "transport", "automotive", "logistics", "delivery"],
    "cybersecurity": ["cybersecurity", "security", "cyber security", "infosec", "cyber"],
    "gaming": ["gaming", "games", "esports", "video games", "entertainment"],
    "climate": ["climate", "cleantech", "climate tech", "sustainability", "green tech"],
    "foodtech": ["foodtech", "food", "food tech", "agriculture", "agtech"],
}


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

    def _filter_by_company_names(self, df: pd.DataFrame, company_names: list) -> pd.DataFrame:
        """
        Filter DataFrame to only include specific companies by name.
        Uses normalized matching to handle spacing/capitalization differences.

        Args:
            df: Portfolio DataFrame
            company_names: List of company names to keep

        Returns:
            Filtered DataFrame
        """
        if not company_names or df.empty:
            return df

        company_col = self._find_column(df, "company name")
        if not company_col:
            return df

        # Normalize company names for matching
        normalized_targets = {
            name.lower().replace(" ", "").replace("-", "")
            for name in company_names
        }

        normalized_col = (
            df[company_col].astype(str)
            .str.lower()
            .str.replace(" ", "", regex=False)
            .str.replace("-", "", regex=False)
        )

        mask = normalized_col.isin(normalized_targets)
        result = df[mask]

        logger.debug(
            f"Filtered by company names: {len(result)}/{len(df)} matched",
            target_names=company_names,
        )

        return result

    def _expand_vertical_filter(self, user_value: str) -> list:
        """
        Expand a vertical/sector filter to include synonyms.

        E.g., "finance" → ["fintech", "financial", "finance", "banking", ...]

        Args:
            user_value: The value the user searched for

        Returns:
            List of synonyms to search for (including original value)
        """
        user_value_lower = user_value.lower().strip()

        # Check if user value matches any synonym in our mappings
        for main_vertical, synonyms in VERTICAL_SYNONYMS.items():
            if user_value_lower in synonyms:
                logger.debug(f"Expanded vertical '{user_value}' to synonyms: {synonyms}")
                return synonyms

        # If no match, return original value
        return [user_value]

    def process_portfolio_aggregation(
        self, df: pd.DataFrame, aggregation_type: str, aggregation_field: str, filters: Dict[str, Any] = None, company_names: list = None
    ) -> Dict[str, Any]:
        """
        Calculate aggregations across portfolio companies.

        Args:
            df: Portfolio DataFrame
            aggregation_type: Type of aggregation (average, median, sum, min, max, count)
            aggregation_field: Field to aggregate (investment, return, valuation, etc.)
            filters: Optional filters to apply before aggregation

        Returns:
            Dictionary with aggregation result
        """
        try:
            if df.empty:
                return {"error": "No portfolio data available"}

            # Filter to RV portfolio only
            df = self._filter_rv_portfolio(df)

            if df.empty:
                return {"error": "No RV portfolio companies found"}

            # Filter by specific company names (from previous result context)
            if company_names:
                df = self._filter_by_company_names(df, company_names)

            # Apply additional filters if provided
            if filters:
                for key, value in filters.items():
                    filter_col = self._find_column(df, key)
                    if filter_col:
                        df = df[df[filter_col].astype(str).str.contains(str(value), case=False, na=False)]

            # Find the aggregation column
            agg_col = self._find_column(df, aggregation_field)

            if not agg_col:
                return {
                    "error": f"Field '{aggregation_field}' not found. Available fields: {', '.join(df.columns[:10])}"
                }

            # Clean and convert to numeric
            df_clean = df.copy()
            df_clean[agg_col] = (
                df_clean[agg_col]
                .astype(str)
                .str.replace('$', '', regex=False)
                .str.replace('K', '', regex=False)
                .str.replace('M', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.replace('x', '', regex=False)  # For returns like "7.1x"
                .str.strip()
            )

            # Convert to numeric
            df_clean[agg_col] = pd.to_numeric(df_clean[agg_col], errors='coerce')

            # Drop NaN values
            df_clean = df_clean.dropna(subset=[agg_col])

            if df_clean.empty:
                return {"error": f"No valid numeric data found for '{aggregation_field}'"}

            # Perform aggregation
            aggregation_type_lower = aggregation_type.lower()

            if aggregation_type_lower in ['average', 'avg', 'mean']:
                result_value = df_clean[agg_col].mean()
                agg_name = "Average"
            elif aggregation_type_lower == 'median':
                result_value = df_clean[agg_col].median()
                agg_name = "Median"
            elif aggregation_type_lower in ['sum', 'total']:
                result_value = df_clean[agg_col].sum()
                agg_name = "Total"
            elif aggregation_type_lower in ['min', 'minimum', 'smallest']:
                result_value = df_clean[agg_col].min()
                agg_name = "Minimum"
            elif aggregation_type_lower in ['max', 'maximum', 'largest']:
                result_value = df_clean[agg_col].max()
                agg_name = "Maximum"
            elif aggregation_type_lower == 'count':
                result_value = len(df_clean)
                agg_name = "Count"
            else:
                return {"error": f"Unsupported aggregation type: {aggregation_type}"}

            # Calculate sum for calculation explanations (useful for showing "total ÷ count = average")
            total_sum = df_clean[agg_col].sum()

            logger.info(
                "Processed portfolio aggregation",
                aggregation_type=aggregation_type,
                field=aggregation_field,
                result=result_value,
                data_points=len(df_clean),
            )

            return {
                "aggregation": agg_name,
                "field": aggregation_field,
                "field_column": agg_col,
                "value": result_value,
                "data_points": len(df_clean),
                "total_sum": total_sum,  # For calculation explanations
                "total_portfolio": len(df),
            }

        except Exception as e:
            logger.error("Error processing portfolio aggregation", error=str(e), exc_info=True)
            return {"error": f"Error calculating aggregation: {str(e)}"}

    def process_time_series(self, df: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """
        Extract time series data for one or more metrics.

        Args:
            df: Fund metrics DataFrame
            metric: Metric name or comma-separated names (TVPI, DPI, or "TVPI,DPI")

        Returns:
            Dictionary with time series data for all requested metrics
        """
        try:
            if df.empty:
                return {"error": "No fund metrics data available"}

            # Handle comma-separated metrics (e.g., "TVPI,DPI")
            metrics = [m.strip() for m in metric.split(',')]

            # Process each metric separately
            all_series = {}
            for single_metric in metrics:
                result = self._process_single_metric_time_series(df, single_metric)
                if "error" in result:
                    return result  # Return error if any metric fails
                all_series[single_metric] = result

            # If only one metric, return it directly (backward compatibility)
            if len(all_series) == 1:
                return list(all_series.values())[0]

            # For multiple metrics, return combined result
            return {
                "metrics": list(all_series.keys()),
                "series": all_series
            }

        except Exception as e:
            logger.error("Error processing time series", metric=metric, error=str(e))
            return {"error": f"Error processing time series: {str(e)}"}

    def _process_single_metric_time_series(self, df: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """Process time series for a single metric."""
        try:
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
                return {"error": f"Metric '{metric}' not found in data. Available metrics: {', '.join(df.columns[1:])}"}

            # Get the time period column (first column)
            period_col = df.columns[0]

            # Filter out rows with None/NaN/empty values for the metric
            valid_df = df[df[metric_col].notna() & (df[metric_col] != '') & (df[metric_col] != 'None')]

            if valid_df.empty:
                return {"error": f"No valid data found for {metric}"}

            # Find "Total up to Today" row (current state) FIRST before filtering
            current_keywords = ['total up to today']
            current_row = None
            for keyword in current_keywords:
                matching = valid_df[valid_df[period_col].astype(str).str.lower() == keyword]
                if not matching.empty:
                    current_row = matching.iloc[0]
                    break

            # Exclude summary rows and specific date formats (e.g., "3/31/2024")
            # Keep only quarterly periods (Q1'21, Q2'22, etc.) and year ranges (2019-2020, 2021, etc.)
            exclude_keywords = ['carry', 'average', 'summary', 'plan', 'diff', 'stage', 'region', 'year', 'total', 'commitments', '/']
            time_series_df = valid_df[
                ~valid_df[period_col].astype(str).str.lower().str.contains('|'.join(exclude_keywords), na=False)
            ]

            if time_series_df.empty:
                # If filtering removed everything, return all valid data
                time_series_df = valid_df

            # Build time series result from historical data
            time_series = []
            for _, row in time_series_df.iterrows():
                time_series.append({
                    "period": row[period_col],
                    "value": row[metric_col]
                })

            # Append current state ("Total up to Today") as the final data point
            if current_row is not None:
                # Check if it's not already in the time series
                if not any(item["period"] == current_row[period_col] for item in time_series):
                    time_series.append({
                        "period": current_row[period_col],
                        "value": current_row[metric_col]
                    })

            return {
                "metric": metric,
                "metric_column": metric_col,
                "data_points": len(time_series),
                "time_series": time_series
            }

        except Exception as e:
            logger.error("Error processing time series", metric=metric, error=str(e))
            return {"error": f"Error processing time series: {str(e)}"}

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
                # Filter out rows with None/NaN/empty values
                valid_df = df[df[metric_col].notna() & (df[metric_col] != '') & (df[metric_col] != 'None')]

                if valid_df.empty:
                    return {"error": f"No valid data found for {metric}"}

                # Prefer "Total up to Today" or similar current summary rows
                period_col = df.columns[0]
                current_keywords = ['total up to today', 'current', 'latest', 'today']

                for keyword in current_keywords:
                    matching = valid_df[valid_df[period_col].astype(str).str.lower().str.contains(keyword, na=False)]
                    if not matching.empty:
                        value = matching[metric_col].iloc[-1]
                        period = matching[period_col].iloc[-1]
                        logger.info(f"Found current metric using keyword '{keyword}'", metric=metric, period=period)
                        return {
                            "metric": metric,
                            "value": value,
                            "period": period,
                        }

                # Otherwise, use the last valid row
                value = valid_df[metric_col].iloc[-1]
                period = valid_df.iloc[-1].get(df.columns[0], "Latest")  # First column usually has period
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

        # Strategy 2: Handle common aliases — checked BEFORE "ends with" to avoid wrong matches.
        # e.g. "Initial Investment post valuation" ends with "valuation" and would incorrectly
        # win over "Last round post-money valuation, $M" without this ordering.
        # Comprehensive column mapping system - maps user filter terms to Google Sheets columns
        aliases = {
            # Financial metrics
            "return": ["investment (w/o fees) return", "investment return", "return", "multiple", "x return"],
            "investment": ["rv investment, $k", "rv investment", "investment amount", "check size", "invested"],
            "valuation": ["last round post-money valuation", "post valuation", "post-money valuation", "valuation", "post money"],

            # Company identification
            "company": ["company name", "name", "portfolio company"],
            "company_name": ["company name", "name"],

            # Geographic/Location - Critical for queries like "french companies" or "companies in europe"
            "country": ["country", "hq country", "headquarters country", "hq", "headquarters", "location"],
            "region": ["region", "geography", "hq", "headquarters", "location"],
            "hq": ["hq", "headquarters", "hq location", "location", "office"],
            "location": ["location", "hq", "headquarters", "region", "geography"],

            # Sector/Industry - Critical for queries like "fintech companies" or "ai companies"
            "vertical": ["vertical", "sector", "industry", "category", "space"],
            "sector": ["sector", "vertical", "industry", "category"],
            "industry": ["industry", "vertical", "sector", "category"],

            # Stage/Round
            "stage": ["stage", "investment stage", "round stage", "series", "round"],
            "round": ["round", "last round", "funding round", "stage"],

            # Temporal/Dates - For queries about timing
            "investment_date": ["investment date", "date invested", "investment year", "year invested", "invested date"],
            "investment date": ["investment date", "date invested", "investment year", "year invested", "invested date"],
            "founded": ["founded", "founding date", "year founded", "founded year", "inception"],
            "last_round_date": ["last round date", "last funding date", "last raise date", "latest round"],
            "last round date": ["last round date", "last funding date", "last raise date", "latest round"],
            "years_since_last_financing": ["years since last financing", "years since funding", "years without funding", "time since last round"],
            "years since last financing": ["years since last financing", "years since funding", "years without funding", "time since last round"],

            # Status fields
            "status": ["status", "company status", "investment status"],
            "is_rv_portfolio": ["is rv portfolio", "rv portfolio", "portfolio status", "in portfolio"],

            # Exit information
            "exit_date": ["exit date", "exit year", "date exited", "exited"],
            "exit_type": ["exit type", "exit method", "exit strategy"],
        }

        for alias, variations in aliases.items():
            if alias in search_lower:
                for variation in variations:
                    for col in df.columns:
                        if variation in col.lower():
                            logger.debug(f"Matched '{search_term}' to column '{col}' via alias '{variation}'")
                            return col

        # Strategy 3: Column ends with search term
        for col in df.columns:
            if col.lower().strip().endswith(search_lower):
                return col

        # Strategy 4: Broad substring match (as fallback only)
        for col in df.columns:
            if search_lower in col.lower():
                logger.debug(f"Matched '{search_term}' to column '{col}' via substring")
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
            'investment date',  # Added for "last investments" queries
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
        self, df: pd.DataFrame, sort_by: str, limit: int = 5, show_all_details: bool = False, ascending: bool = False, company_names: list = None
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

            # Filter by specific company names (from previous result context)
            if company_names:
                df = self._filter_by_company_names(df, company_names)

            # Make a copy to avoid modifying original
            df = df.copy()

            # Find the sort column using flexible matching
            sort_col = self._find_column(df, sort_by)

            if not sort_col:
                logger.warning("Sort column not found", sort_by=sort_by, available=list(df.columns))
                # Return first N rows
                return df.head(limit)

            logger.debug(f"Sorting by column: '{sort_col}' for search term: '{sort_by}', ascending={ascending}")

            # Check if this is a date column
            is_date_column = 'date' in sort_col.lower()

            if is_date_column:
                # Handle date sorting
                # Try to parse dates - pd.to_datetime handles many formats
                df[sort_col + '_parsed'] = pd.to_datetime(df[sort_col], errors='coerce', format='%b-%Y')

                # If that didn't work, try without format specification
                if df[sort_col + '_parsed'].isna().all():
                    df[sort_col + '_parsed'] = pd.to_datetime(df[sort_col], errors='coerce')

                # Drop rows where date parsing completely failed AND original value is empty
                df = df[df[sort_col].notna() & (df[sort_col].astype(str).str.strip() != '')]

                # Sort by parsed date if available, otherwise by string
                if not df[sort_col + '_parsed'].isna().all():
                    # Sort by parsed date
                    result = (
                        df.sort_values(by=sort_col + '_parsed', ascending=ascending)
                        .head(limit)
                        .reset_index(drop=True)
                    )
                    # Remove the temporary parsed column
                    result = result.drop(columns=[sort_col + '_parsed'])
                else:
                    # Fallback to string sorting
                    result = (
                        df.sort_values(by=sort_col, ascending=ascending)
                        .head(limit)
                        .reset_index(drop=True)
                    )
            else:
                # Handle numeric sorting (original logic)
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

    def process_portfolio_list(self, df: pd.DataFrame, filters: Dict[str, Any], show_all_details: bool = False, company_names: list = None) -> pd.DataFrame:
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

            logger.debug(f"Starting portfolio_list with {len(df)} total companies")

            # Filter to RV portfolio only
            result = self._filter_rv_portfolio(df.copy())
            logger.debug(f"After RV portfolio filter: {len(result)} companies remain")

            # Filter by specific company names (from previous result context)
            if company_names:
                result = self._filter_by_company_names(result, company_names)
                logger.debug(f"After company_names filter: {len(result)} companies remain")

            # Apply each filter
            for key, value in filters.items():
                # Find matching column using flexible matching
                filter_col = self._find_column(result, key)

                if filter_col:
                    # Check if this is a numeric comparison field (e.g., "years since last financing")
                    is_numeric_field = any(keyword in filter_col.lower() for keyword in ['years', 'year', 'age', 'duration', 'time since'])

                    # Check if this is a vertical/sector/industry field
                    is_vertical_field = any(keyword in filter_col.lower() for keyword in ['vertical', 'sector', 'industry', 'category'])

                    # Check if this is a company name field
                    is_company_field = any(keyword in filter_col.lower() for keyword in ['company', 'name'])

                    if is_numeric_field:
                        # Try numeric comparison (greater than or equal)
                        try:
                            # Clean and convert column to numeric
                            numeric_col = pd.to_numeric(result[filter_col], errors='coerce')
                            threshold = float(str(value).replace('+', '').strip())

                            # Filter for values >= threshold
                            result = result[numeric_col >= threshold]
                            logger.debug(f"Applied numeric filter: {filter_col} >= {threshold}")
                        except (ValueError, TypeError):
                            # If numeric conversion fails, fall back to string matching
                            result = result[
                                result[filter_col].astype(str).str.contains(str(value), case=False, na=False)
                            ]
                    elif is_vertical_field:
                        # Expand vertical filter with synonyms (e.g., "finance" → ["fintech", "financial", "finance", ...])
                        synonyms = self._expand_vertical_filter(str(value))

                        # Create OR filter: match if ANY synonym is found in the column value
                        mask = pd.Series([False] * len(result), index=result.index)
                        for synonym in synonyms:
                            mask |= result[filter_col].astype(str).str.contains(synonym, case=False, na=False)

                        result = result[mask]
                        logger.debug(f"Applied vertical filter: {filter_col} matches any of {synonyms}")
                    elif is_company_field:
                        # Normalize both sides to handle spacing/capitalization differences
                        # e.g., "ElevenLabs" matches "Eleven Labs", "Eleven Labs1", etc.
                        normalized_value = str(value).lower().replace(" ", "").replace("-", "")
                        normalized_col = (
                            result[filter_col].astype(str)
                            .str.lower()
                            .str.replace(" ", "", regex=False)
                            .str.replace("-", "", regex=False)
                        )
                        result = result[normalized_col.str.contains(normalized_value, na=False)]
                        logger.debug(f"Applied company name filter (normalized): '{value}' → '{normalized_value}', found {len(result)} matches")
                    else:
                        # Apply string filter (case-insensitive contains)
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

    def _drop_hidden_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove columns that should never be shown to users."""
        cols_to_drop = [c for c in HIDDEN_COLUMNS if c in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
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
            result = self.process_portfolio_ranking(
                portfolio_df, sort_by, limit, show_all_details=intent.show_all_details, ascending=intent.ascending,
                company_names=intent.company_names or None,
            )
            if isinstance(result, pd.DataFrame):
                result = self._drop_hidden_columns(result)
            return result

        elif intent.query_type == QueryType.PORTFOLIO_LIST:
            result = self.process_portfolio_list(
                portfolio_df, intent.filters, show_all_details=intent.show_all_details,
                company_names=intent.company_names or None,
            )
            if isinstance(result, pd.DataFrame):
                result = self._drop_hidden_columns(result)
            return result

        elif intent.query_type == QueryType.COMPANY_DETAIL:
            if intent.company_name:
                filters = {"company_name": intent.company_name}
                result = self.process_portfolio_list(
                    portfolio_df, filters, show_all_details=True
                )
                if isinstance(result, pd.DataFrame):
                    result = self._drop_hidden_columns(result)
                # Narrow columns if user asked about specific fields
                if intent.specific_fields and isinstance(result, pd.DataFrame) and not result.empty:
                    company_col = self._find_column(result, "company name")
                    selected = [company_col] if company_col else []
                    for field in intent.specific_fields:
                        col = self._find_column(result, field)
                        if col and col not in selected:
                            selected.append(col)
                    if len(selected) <= 1:
                        # All requested fields were missing — tell the AI explicitly
                        return {"info": f"No data found for the requested field(s) ({', '.join(intent.specific_fields)}) for {intent.company_name}. The field may not exist or is empty in the sheet."}
                    result = result[selected]
                return result
            return {"error": "No company name specified"}

        elif intent.query_type == QueryType.TIME_SERIES:
            if not intent.metric:
                return {"error": "No metric specified for time series"}
            return self.process_time_series(fund_df, intent.metric)

        elif intent.query_type == QueryType.PORTFOLIO_AGGREGATION:
            if not intent.aggregation_type or not intent.aggregation_field:
                return {"error": "Aggregation type and field must be specified"}
            return self.process_portfolio_aggregation(
                portfolio_df, intent.aggregation_type, intent.aggregation_field, intent.filters,
                company_names=intent.company_names or None,
            )

        else:
            return {"error": "Unknown query type"}


# Global data processor instance
data_processor = DataProcessor()
