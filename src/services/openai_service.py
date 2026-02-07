"""
OpenAI service for query analysis and response generation.
"""

from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info("OpenAI service initialized", model=self.model)

    async def analyze_query_intent(
        self,
        user_question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze user query to extract intent and parameters.

        Args:
            user_question: The user's question
            conversation_history: Previous conversation messages

        Returns:
            Dictionary with query intent and parameters
        """
        try:
            # Build messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """You are a query analyzer for a VC fund metrics bot.
Analyze user questions and extract structured intent.

Available query types:
- fund_metric: Questions about fund-level metrics (TVPI, DPI, IRR, etc.)
- portfolio_ranking: Top N companies by some criteria
- portfolio_list: List companies with filters
- company_detail: Information about a specific company
- time_series: Performance over time
- general_chat: General questions, follow-ups, elaborations, or anything not requiring data lookup

Available fund metrics (use simple names):
- TVPI (Total Value to Paid In)
- DPI (Distributed to Paid In)
- IRR (Internal Rate of Return)
- Investments
- Portfolio Value
- Realised Value

Common portfolio fields for ranking/filtering:
- investment (for RV investment amount in dollars)
- return (for investment return MULTIPLIER, e.g., 7.1x means 7.1 times the investment)
- valuation (for company valuation)
- stage (for investment stage)
- vertical (for industry sector)
- region (for geographic location)
- founded (for founding date)

Extract and return JSON with:
- query_type: one of the types above
- metric: specific metric name (use simple names: TVPI, DPI, IRR, etc.)
- filters: any filters mentioned (sector, stage, etc.)
- sort_by: what to sort by for rankings
- limit: how many results to show
- company_name: specific company if mentioned
- time_period: time period if specified (latest, Q1 2024, etc.)
- show_all_details: true if user explicitly asks for "more details", "full info", "everything", "all columns", etc.; false by default
- ascending: true if user asks for "worst", "lowest", "bottom", "smallest"; false for "top", "best", "highest", "largest" (default: false)

Examples:
"What's our current TVPI?" → {"query_type": "fund_metric", "metric": "TVPI", "time_period": "latest"}
"Top 5 companies by investment amount" → {"query_type": "portfolio_ranking", "sort_by": "investment", "limit": 5, "ascending": false}
"Top companies by return" → {"query_type": "portfolio_ranking", "sort_by": "return", "limit": 5, "ascending": false}
"Worst 5 companies by return" → {"query_type": "portfolio_ranking", "sort_by": "return", "limit": 5, "ascending": true}
"Bottom performers" → {"query_type": "portfolio_ranking", "sort_by": "return", "limit": 5, "ascending": true}
"Show fintech companies" → {"query_type": "portfolio_list", "filters": {"vertical": "fintech"}, "show_all_details": false}
"Show me more details about the top companies" → {"query_type": "portfolio_ranking", "limit": 5, "show_all_details": true}
"Can you elaborate on that?" → {"query_type": "general_chat"}
"What does TVPI mean?" → {"query_type": "general_chat"}
""",
                }
            ]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-4:])  # Last 4 messages for context

            # Add current question
            messages.append({"role": "user", "content": user_question})

            # Call OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)

            logger.debug("Analyzed query intent", intent=result)
            return result

        except Exception as e:
            logger.error("Error analyzing query intent", error=str(e))
            # Return a default unknown intent
            return {
                "query_type": "unknown",
                "confidence": 0.0,
            }

    async def generate_response(
        self,
        data: Any,
        original_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate a natural language response from processed data.

        Args:
            data: Processed data to present
            original_query: The user's original question
            conversation_history: Previous conversation messages

        Returns:
            Natural language response
        """
        try:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant for a VC fund.
Present data clearly and concisely. Use Telegram markdown formatting:
- *bold* for emphasis
- `code` for numbers/metrics
- Lists for multiple items

IMPORTANT FORMATTING RULES:
- "Investment Return" or "return" field is a MULTIPLIER (e.g., 7.1 means 7.1x return), NOT dollars
  Display as "7.1x" or "7.1 times", NEVER as "$7.1K"
- "RV Investment" is in dollars, display as "$145K" or similar
- "Valuation" is in dollars/millions, display with $ and M/K suffix

Keep responses under 4000 characters (Telegram limit).
If data is empty or missing, say so politely and suggest alternatives.
""",
                }
            ]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-2:])  # Last 2 messages

            # Add current request
            data_str = str(data) if data is not None else "No data found"
            messages.append({
                "role": "user",
                "content": f"User asked: '{original_query}'\n\nData: {data_str}\n\nGenerate a helpful response in Telegram markdown format.",
            })

            # Call OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            result = response.choices[0].message.content

            logger.debug("Generated response", length=len(result))
            return result

        except Exception as e:
            logger.error("Error generating response", error=str(e))
            return "Sorry, I encountered an error generating the response. Please try again."


# Global OpenAI service instance
openai_service = OpenAIService()
