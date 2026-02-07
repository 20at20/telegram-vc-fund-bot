#!/usr/bin/env python3
"""
Test script to debug portfolio data access.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor


async def test_portfolio():
    """Test fetching portfolio data."""
    print("\n" + "="*60)
    print("TESTING PORTFOLIO DATA ACCESS")
    print("="*60)

    print(f"\nSheet ID: {settings.portfolio_sheet_id}")
    print(f"Range: {settings.portfolio_range}")

    try:
        print("\n📊 Fetching portfolio data...")
        df = await sheets_service.get_portfolio_data()

        print(f"\n✅ Data fetched successfully!")
        print(f"   Total rows: {len(df)}")
        print(f"   Total columns: {len(df.columns)}")

        print(f"\n📋 All Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. '{col}'")

        if not df.empty:
            print(f"\n📊 First Row Sample:")
            first_row = df.iloc[0]
            for col in df.columns[:10]:  # Show first 10 columns
                print(f"   {col}: {first_row[col]}")

            print(f"\n🔍 Testing portfolio ranking (top 5 by investment)...")
            result = data_processor.process_portfolio_ranking(
                df,
                sort_by="investment",
                limit=5
            )

            print(f"\n   Result type: {type(result)}")
            print(f"   Result rows: {len(result) if hasattr(result, '__len__') else 'N/A'}")

            if hasattr(result, 'columns'):
                print(f"   Result columns: {list(result.columns)}")
                print(f"\n   Top 5 companies:")
                for i, row in result.iterrows():
                    company_col = data_processor._find_column(result, 'company name')
                    investment_col = data_processor._find_column(result, 'investment')
                    if company_col and investment_col:
                        print(f"      {i+1}. {row[company_col]}: {row[investment_col]}")

        else:
            print("\n❌ DataFrame is empty! No data returned.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_portfolio())
