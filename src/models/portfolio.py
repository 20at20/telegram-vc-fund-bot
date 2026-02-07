"""
Portfolio company data models.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class PortfolioCompany(BaseModel):
    """Portfolio company information."""

    company_name: str = Field(..., description="Name of the portfolio company")
    investment_date: Optional[date] = Field(None, description="Date of investment")
    investment_amount: Optional[float] = Field(None, description="Amount invested")
    sector: Optional[str] = Field(None, description="Industry sector")
    stage: Optional[str] = Field(None, description="Investment stage (Seed, Series A, etc.)")
    valuation: Optional[float] = Field(None, description="Current valuation")
    status: Optional[str] = Field(None, description="Investment status (Active, Exited, etc.)")

    class Config:
        extra = "allow"  # Allow additional fields from user's sheet
