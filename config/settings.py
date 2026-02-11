"""
Configuration management using Pydantic BaseSettings.
All environment variables and application settings are defined here.
"""

import json
import os
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Configuration
    telegram_bot_token: str = Field(..., description="Telegram bot token from @BotFather")
    allowed_telegram_ids: List[int] = Field(
        ..., description="List of authorized Telegram user IDs"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4-turbo-preview", description="OpenAI model to use"
    )

    # Google Sheets Configuration
    google_credentials_file: str = Field(
        default="config/credentials/google_service_account.json",
        description="Path to Google service account JSON file",
    )
    fund_metrics_sheet_id: str = Field(..., description="Google Sheet ID for fund metrics")
    fund_metrics_range: str = Field(
        default="Summary!A1:Z100", description="Cell range for fund metrics"
    )
    portfolio_sheet_id: str = Field(..., description="Google Sheet ID for portfolio")
    portfolio_range: str = Field(
        default="Portfolio!A1:Z100", description="Cell range for portfolio"
    )

    # Deals Pipeline Sheet Configuration
    deals_sheet_id: str = Field(default="", description="Google Sheet ID for deals pipeline")
    deals_range: str = Field(
        default="Sheet1!A1:G200", description="Cell range for deals data"
    )

    # For Railway deployment (optional)
    google_service_account_json: str | None = Field(
        default=None, description="Google service account JSON as string"
    )

    # Application Settings
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")
    rate_limit_per_user: int = Field(
        default=20, description="Max queries per user per hour"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    # Web App Configuration
    web_password: str = Field(
        default="changeme", description="Password for web chat UI"
    )

    # MCP Configuration
    mcp_config_file: str = Field(
        default="mcp_config.json", description="Path to MCP configuration file"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("allowed_telegram_ids", mode="before")
    @classmethod
    def parse_telegram_ids(cls, v):
        """Parse Telegram IDs from string or list."""
        if isinstance(v, str):
            # Remove brackets and parse as list of integers
            v = v.strip("[]").replace(" ", "")
            return [int(id_str) for id_str in v.split(",") if id_str]
        return v

    def setup_google_credentials(self):
        """
        Setup Google credentials file from environment variable if needed.
        This is useful for Railway deployment where we store JSON as env var.
        """
        if self.google_service_account_json:
            # Create credentials directory if it doesn't exist
            os.makedirs(os.path.dirname(self.google_credentials_file), exist_ok=True)

            # Write JSON to file
            with open(self.google_credentials_file, "w") as f:
                # Handle both string and dict formats
                if isinstance(self.google_service_account_json, str):
                    credentials_dict = json.loads(self.google_service_account_json)
                else:
                    credentials_dict = self.google_service_account_json
                json.dump(credentials_dict, f, indent=2)


# Global settings instance
settings = Settings()

# Setup Google credentials if provided via environment variable
settings.setup_google_credentials()
