"""
Fund performance metrics data models.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class FundMetric(BaseModel):
    """Single fund performance metric for a given period."""

    period: str = Field(..., description="Quarter or period (e.g., Q1 2024)")
    date: Optional[date] = Field(None, description="Date of the metric")
    tvpi: Optional[float] = Field(None, description="Total Value to Paid-In")
    dpi: Optional[float] = Field(None, description="Distributed to Paid-In")
    rvpi: Optional[float] = Field(None, description="Residual Value to Paid-In")
    irr: Optional[float] = Field(None, description="Internal Rate of Return")
    moic: Optional[float] = Field(None, description="Multiple on Invested Capital")

    class Config:
        extra = "allow"  # Allow additional fields from user's sheet
