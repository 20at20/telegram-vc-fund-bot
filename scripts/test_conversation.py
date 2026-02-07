#!/usr/bin/env python3
"""
Test script to verify conversation context works.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer
from src.services.response_generator import response_generator


async def test_conversation():
    """Test conversation with context."""
    print("\n" + "="*60)
    print("TESTING CONVERSATION CONTEXT")
    print("="*60)

    sheets_service.clear_cache()
    fund_df = await sheets_service.get_fund_metrics()
    portfolio_df = await sheets_service.get_portfolio_data()

    # Simulate conversation history
    conversation_history = []

    queries = [
        "give me total investment and number of investments",
        "total investment sum?",
        "divide these 2 numbers",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")

        # Analyze with conversation history
        intent = await query_analyzer.analyze(query, conversation_history)
        print(f"Query type: {intent.query_type}")

        # Process
        processed_data = data_processor.process_query(intent, fund_df, portfolio_df)

        # Generate response with conversation history
        response = await response_generator.generate(
            processed_data, query, conversation_history
        )

        print(f"\nBot Response:")
        print(response)

        # Add to conversation history
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": response})

        # Keep only last 10 messages (5 exchanges) - enough for context
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]

    print(f"\n{'='*60}")
    print("Final conversation history:")
    for msg in conversation_history:
        role = msg['role'].upper()
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"{role}: {content}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_conversation())
