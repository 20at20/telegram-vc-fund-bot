#!/usr/bin/env python3
"""
Test script to verify calculation explanations work correctly.
Tests the specific scenario: "average check" → "how you calculated it?"
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer
from src.services.response_generator import response_generator


async def test_calculation_explanation():
    """Test that bot explains how it calculated results."""
    print("\n" + "="*60)
    print("TESTING CALCULATION EXPLANATIONS")
    print("="*60)

    sheets_service.clear_cache()
    fund_df = await sheets_service.get_fund_metrics()
    portfolio_df = await sheets_service.get_portfolio_data()

    # Simulate conversation
    conversation_history = []

    queries = [
        "average check",
        "how you calculated it?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")

        # Analyze
        intent = await query_analyzer.analyze(query, conversation_history)
        print(f"\nQuery type: {intent.query_type}")
        if hasattr(intent, 'aggregation_type') and intent.aggregation_type:
            print(f"Aggregation: {intent.aggregation_type} of {intent.aggregation_field}")

        # Process
        processed_data = data_processor.process_query(intent, fund_df, portfolio_df)

        # Show processed data structure
        if isinstance(processed_data, dict):
            print(f"\nProcessed data:")
            for key, value in processed_data.items():
                print(f"  {key}: {value}")

        # Generate response
        response = await response_generator.generate(
            processed_data, query, conversation_history
        )

        print(f"\n💬 Bot Response:")
        print(response)

        # Add to history
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": response})

    print(f"\n{'='*60}")
    print("✅ TEST EXPECTATIONS:")
    print("1. First response should include calculation formula")
    print("   Example: 'Average check: $237.63K (total $14,970.60K ÷ 63 companies)'")
    print("2. Second response should explain methodology from conversation history")
    print("   Example: 'I calculated by dividing total investment by number of companies'")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_calculation_explanation())
