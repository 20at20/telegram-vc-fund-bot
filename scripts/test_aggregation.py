#!/usr/bin/env python3
"""
Test script for portfolio aggregation queries.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer
from src.services.response_generator import response_generator


async def test_aggregation():
    """Test aggregation queries."""
    print("\n" + "="*60)
    print("TESTING PORTFOLIO AGGREGATION QUERIES")
    print("="*60)

    # Test queries
    queries = [
        "What's our average check size?",
        "Total invested capital?",
        "What's our average return?",
        "Median return across portfolio?",
    ]

    fund_df = await sheets_service.get_fund_metrics()
    portfolio_df = await sheets_service.get_portfolio_data()

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Analyze intent
        intent = await query_analyzer.analyze(query, None)
        print(f"\n🔍 Intent Analysis:")
        print(f"   Query type: {intent.query_type}")
        print(f"   Aggregation type: {intent.aggregation_type}")
        print(f"   Aggregation field: {intent.aggregation_field}")

        # Process data
        result = data_processor.process_query(intent, fund_df, portfolio_df)

        print(f"\n📊 Result:")
        if isinstance(result, dict):
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   {result['aggregation']} {result['field']}: {result['value']}")
                print(f"   Data points: {result['data_points']}")
                print(f"   Field column: {result['field_column']}")

        # Generate response
        response = await response_generator.generate(result, query, None)
        print(f"\n💬 Bot Response:")
        print(f"   {response}")


if __name__ == "__main__":
    asyncio.run(test_aggregation())
