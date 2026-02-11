"""
Query intent models for parsing and understanding user questions.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryType(str, Enum):
    """Types of queries the bot can handle."""

    FUND_METRIC = "fund_metric"  # Questions about fund-level metrics
    PORTFOLIO_RANKING = "portfolio_ranking"  # Top N companies
    PORTFOLIO_LIST = "portfolio_list"  # List companies with filters
    COMPANY_DETAIL = "company_detail"  # Details about specific company
    TIME_SERIES = "time_series"  # Performance over time
    PORTFOLIO_AGGREGATION = "portfolio_aggregation"  # Aggregate calculations (average, total, median)
    GENERAL_CHAT = "general_chat"  # General questions, elaboration requests
    UNKNOWN = "unknown"  # Couldn't understand the query


class QueryIntent(BaseModel):
    """Structured representation of user query intent."""

    query_type: QueryType = Field(..., description="Type of query")
    metric: Optional[str] = Field(None, description="Specific metric requested (e.g., TVPI, DPI, IRR)")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filters to apply")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    limit: Optional[int] = Field(None, description="Maximum number of results")
    company_name: Optional[str] = Field(None, description="Specific company name")
    time_period: Optional[str] = Field(None, description="Time period (latest, Q1 2024, etc.)")
    aggregation_type: Optional[str] = Field(None, description="Type of aggregation (average, median, sum, min, max, count)")
    aggregation_field: Optional[str] = Field(None, description="Field to aggregate (investment, return, valuation, etc.)")
    show_all_details: bool = Field(default=False, description="Whether to show all columns or just key ones")
    ascending: bool = Field(default=False, description="Sort ascending (True for worst/lowest/bottom, False for top/best/highest)")
    company_names: List[str] = Field(default_factory=list, description="Specific company names to filter by (from previous result context)")
    confidence: float = Field(default=1.0, description="Confidence in intent parsing")

    class Config:
        use_enum_values = True
