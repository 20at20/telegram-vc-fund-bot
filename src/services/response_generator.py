"""
Response generator service for formatting data into user-friendly messages.
"""

import pandas as pd
from typing import Any, Dict, List, Optional

from src.services.openai_service import openai_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseGenerator:
    """Generates natural language responses from processed data."""

    MAX_MESSAGE_LENGTH = 4000  # Telegram message limit is 4096

    async def generate(
        self,
        data: Any,
        original_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate a user-friendly response from processed data.

        Args:
            data: Processed data (DataFrame, dict, or error message)
            original_query: The user's original question
            conversation_history: Previous conversation messages

        Returns:
            Formatted response string
        """
        try:
            # Handle error responses
            if isinstance(data, dict) and "error" in data:
                return f"❌ {data['error']}\n\nPlease try rephrasing your question or use /help for examples."

            # Format based on data type
            if isinstance(data, pd.DataFrame):
                formatted_data = self._format_dataframe(data)
            elif isinstance(data, dict):
                formatted_data = self._format_dict(data)
            else:
                formatted_data = str(data)

            # Use OpenAI to generate natural language response
            response = await openai_service.generate_response(
                formatted_data, original_query, conversation_history
            )

            # Ensure response fits in Telegram message
            if len(response) > self.MAX_MESSAGE_LENGTH:
                response = response[:self.MAX_MESSAGE_LENGTH - 50] + "\n\n...(truncated)"

            return response

        except Exception as e:
            logger.error("Error generating response", error=str(e))
            return "Sorry, I encountered an error generating the response. Please try again."

    def _format_dataframe(self, df: pd.DataFrame) -> str:
        """Format a DataFrame for display."""
        if df.empty:
            return "No results found."

        # Limit to first 10 rows
        display_df = df.head(10)

        # Convert to readable format
        result = []
        for idx, row in display_df.iterrows():
            row_data = []
            for col, value in row.items():
                if pd.notna(value) and value != "":
                    row_data.append(f"{col}: {value}")
            if row_data:
                result.append("\n".join(row_data))

        formatted = "\n\n".join(result)

        # Add count if there are more rows
        if len(df) > 10:
            formatted += f"\n\n... and {len(df) - 10} more"

        return formatted

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format a dictionary for display."""
        result = []
        for key, value in data.items():
            if key != "error":
                result.append(f"{key}: {value}")
        return "\n".join(result)


# Global response generator instance
response_generator = ResponseGenerator()
