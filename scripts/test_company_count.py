#!/usr/bin/env python3
"""
Test script to debug company count query.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer


async def test_company_count():
    """Test company count query."""
    print("\n" + "="*60)
    print("TESTING COMPANY COUNT QUERY")
    print("="*60)

    # Analyze the query
    query = "how many companies in portfolio?"
    print(f"\n📝 Query: {query}")

    intent = await query_analyzer.analyze(query, None)
    print(f"\n🔍 Intent Analysis:")
    print(f"   Query type: {intent.query_type}")
    print(f"   Filters: {intent.filters}")
    print(f"   Show all details: {intent.show_all_details}")

    # Fetch data
    portfolio_df = await sheets_service.get_portfolio_data()
    print(f"\n📊 Raw Portfolio Data:")
    print(f"   Total rows: {len(portfolio_df)}")

    # Check "Is RV portfolio?" column
    rv_col = None
    for col in portfolio_df.columns:
        if 'rv portfolio' in col.lower():
            rv_col = col
            break

    if rv_col:
        print(f"\n📋 '{rv_col}' column values:")
        value_counts = portfolio_df[rv_col].value_counts()
        for value, count in value_counts.items():
            print(f"   '{value}': {count} companies")

        # Count only "Yes" values
        yes_count = portfolio_df[portfolio_df[rv_col].astype(str).str.lower().isin(['yes', 'y', 'true', '1'])].shape[0]
        print(f"\n✅ RV Portfolio companies (Yes): {yes_count}")

        # Show some examples of non-RV companies
        non_rv = portfolio_df[~portfolio_df[rv_col].astype(str).str.lower().isin(['yes', 'y', 'true', '1'])]
        print(f"\n❌ Non-RV Portfolio companies: {len(non_rv)}")
        if len(non_rv) > 0:
            print(f"   Examples:")
            company_col = None
            for col in portfolio_df.columns:
                if 'company name' in col.lower():
                    company_col = col
                    break
            if company_col:
                for i, row in non_rv.head(10).iterrows():
                    print(f"      - {row[company_col]}: {row[rv_col]}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_company_count())
