"""
Query analyzer service that parses user questions into structured intents.
"""

from typing import List, Dict, Optional

from src.models.query import QueryIntent, QueryType
from src.services.openai_service import openai_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QueryAnalyzer:
    """Analyzes user queries to extract intent and parameters."""

    async def analyze(
        self,
        user_question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> QueryIntent:
        """
        Analyze a user question to extract structured intent.

        Args:
            user_question: The user's question
            conversation_history: Previous conversation messages

        Returns:
            QueryIntent object with parsed intent and parameters
        """
        try:
            # Use OpenAI to analyze the query
            intent_data = await openai_service.analyze_query_intent(
                user_question, conversation_history
            )

            # Convert to QueryIntent model
            query_type = QueryType(intent_data.get("query_type", "unknown"))

            intent = QueryIntent(
                query_type=query_type,
                metric=intent_data.get("metric"),
                filters=intent_data.get("filters", {}),
                sort_by=intent_data.get("sort_by"),
                limit=intent_data.get("limit"),
                company_name=intent_data.get("company_name"),
                time_period=intent_data.get("time_period", "latest"),
                aggregation_type=intent_data.get("aggregation_type"),
                aggregation_field=intent_data.get("aggregation_field"),
                show_all_details=intent_data.get("show_all_details", False),
                ascending=intent_data.get("ascending", False),
                confidence=intent_data.get("confidence", 1.0),
            )

            logger.info(
                "Analyzed query",
                query=user_question,
                query_type=query_type,
                confidence=intent.confidence,
            )

            return intent

        except Exception as e:
            logger.error("Error analyzing query", error=str(e), query=user_question)
            # Return unknown intent on error
            return QueryIntent(
                query_type=QueryType.UNKNOWN,
                confidence=0.0,
            )


# Global query analyzer instance
query_analyzer = QueryAnalyzer()
