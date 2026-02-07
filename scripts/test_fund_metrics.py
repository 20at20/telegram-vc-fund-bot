#!/usr/bin/env python3
"""
Test script to debug fund metrics data access.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from src.services.sheets_service import sheets_service


async def test_fund_metrics():
    """Test fetching fund metrics data."""
    print("\n" + "="*60)
    print("TESTING FUND METRICS DATA ACCESS")
    print("="*60)

    print(f"\nSheet ID: {settings.fund_metrics_sheet_id}")
    print(f"Range: {settings.fund_metrics_range}")

    try:
        print("\n📊 Fetching fund metrics data...")
        df = await sheets_service.get_fund_metrics()

        print(f"\n✅ Data fetched successfully!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")

        print(f"\n📋 Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. '{col}'")

        if not df.empty:
            print(f"\n📊 First Row of Data:")
            print(df.iloc[0].to_dict())

            print(f"\n🔍 Looking for TVPI column...")
            tvpi_col = None
            for col in df.columns:
                col_lower = col.lower()
                if 'tvpi' in col_lower:
                    tvpi_col = col
                    print(f"   ✅ Found TVPI column: '{col}'")
                    print(f"   Value: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
                    break

            if not tvpi_col:
                print("   ❌ TVPI column not found!")
                print("\n   Available columns:")
                for col in df.columns:
                    print(f"      - '{col}'")

        else:
            print("\n❌ DataFrame is empty! No data returned.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_fund_metrics())
