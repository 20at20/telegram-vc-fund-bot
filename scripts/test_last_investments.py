#!/usr/bin/env python3
"""
Test script for last/recent investments query.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer


async def test_last_investments():
    """Test last investments query."""
    print("\n" + "="*60)
    print("TESTING LAST INVESTMENTS QUERY")
    print("="*60)

    query = "our 3 last investments"
    print(f"\n📝 Query: {query}")

    # Analyze intent
    intent = await query_analyzer.analyze(query, None)
    print(f"\n🔍 Intent Analysis:")
    print(f"   Query type: {intent.query_type}")
    print(f"   Sort by: {intent.sort_by}")
    print(f"   Limit: {intent.limit}")
    print(f"   Ascending: {intent.ascending}")

    # Fetch and process data
    portfolio_df = await sheets_service.get_portfolio_data()

    print(f"\n📊 Available columns:")
    for col in portfolio_df.columns:
        if 'date' in col.lower() or 'investment' in col.lower():
            print(f"   - {col}")

    # Test column matching
    sort_col = data_processor._find_column(portfolio_df, "investment date")
    print(f"\n🔍 Column matching test:")
    print(f"   Search term: 'investment date'")
    print(f"   Matched column: '{sort_col}'")

    if sort_col:
        print(f"\n📅 Sample dates from '{sort_col}':")
        valid_dates = portfolio_df[portfolio_df[sort_col].notna() & (portfolio_df[sort_col] != '')]
        print(f"   Total rows with dates: {len(valid_dates)}")
        print(f"   Sample values:")
        for val in valid_dates[sort_col].head(10):
            print(f"      - {val}")

    # Process the query
    fund_df = await sheets_service.get_fund_metrics()
    result = data_processor.process_query(intent, fund_df, portfolio_df)

    print(f"\n📋 Result:")
    if hasattr(result, '__len__'):
        print(f"   Rows returned: {len(result)}")
        if hasattr(result, 'columns'):
            company_col = data_processor._find_column(result, 'company name')
            date_col = data_processor._find_column(result, 'investment date')
            if company_col and date_col:
                print(f"\n   Companies (most recent first):")
                for i, row in result.iterrows():
                    print(f"      {i+1}. {row[company_col]} - {row[date_col]}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_last_investments())
