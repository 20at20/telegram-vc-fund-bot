#!/usr/bin/env python3
"""
Test script to debug count queries.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer


async def test_counts():
    """Test count queries."""
    print("\n" + "="*60)
    print("TESTING COUNT QUERIES")
    print("="*60)

    # Clear cache to get fresh data
    sheets_service.clear_cache()
    print("\n✅ Cache cleared - fetching fresh data\n")

    # Fetch fresh data
    portfolio_df = await sheets_service.get_portfolio_data()
    fund_df = await sheets_service.get_fund_metrics()

    print(f"📊 Raw Portfolio Data:")
    print(f"   Total rows (after cleaning): {len(portfolio_df)}")

    # Check RV portfolio filter
    rv_col = None
    for col in portfolio_df.columns:
        if 'rv portfolio' in col.lower():
            rv_col = col
            break

    if rv_col:
        print(f"\n📋 '{rv_col}' column breakdown:")
        value_counts = portfolio_df[rv_col].value_counts()
        for value, count in value_counts.items():
            print(f"   '{value}': {count} companies")

        rv_count = len(portfolio_df[portfolio_df[rv_col].astype(str).str.lower().isin(['yes', 'y', 'true', '1'])])
        print(f"\n✅ RV Portfolio companies (Yes): {rv_count}")
        print(f"   Expected: 63")
        print(f"   Match: {'✅' if rv_count == 63 else '❌'}")

    # Test "how many companies in portfolio?"
    query1 = "how many companies in portfolio?"
    print(f"\n{'='*60}")
    print(f"Query 1: {query1}")
    print(f"{'='*60}")

    intent1 = await query_analyzer.analyze(query1, None)
    print(f"   Query type: {intent1.query_type}")
    print(f"   Filters: {intent1.filters}")

    result1 = data_processor.process_query(intent1, fund_df, portfolio_df)
    if hasattr(result1, '__len__'):
        print(f"   Result count: {len(result1)}")
        print(f"   Expected: 63")

    # Test "how many deals we made?"
    query2 = "how many deals we made?"
    print(f"\n{'='*60}")
    print(f"Query 2: {query2}")
    print(f"{'='*60}")

    intent2 = await query_analyzer.analyze(query2, None)
    print(f"   Query type: {intent2.query_type}")
    print(f"   Metric: {intent2.metric}")
    print(f"   Aggregation type: {intent2.aggregation_type}")
    print(f"   Aggregation field: {intent2.aggregation_field}")
    print(f"   Filters: {intent2.filters}")

    result2 = data_processor.process_query(intent2, fund_df, portfolio_df)
    print(f"   Result: {result2}")

    # Check fund metrics "Investments #"
    print(f"\n📊 Fund Metrics - Investments #:")
    inv_col = None
    for col in fund_df.columns:
        if 'investment' in col.lower() and '#' in col:
            inv_col = col
            break

    if inv_col:
        print(f"   Column: '{inv_col}'")
        total_row = fund_df[fund_df[fund_df.columns[0]].astype(str).str.lower().str.contains('total up to today', na=False)]
        if not total_row.empty:
            print(f"   'Total up to Today': {total_row[inv_col].iloc[0]}")
        print(f"   Expected: 72")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_counts())
