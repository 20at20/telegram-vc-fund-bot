#!/usr/bin/env python3
"""
Test script to check latest TVPI value.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor


async def test_latest_tvpi():
    """Test getting latest TVPI."""
    print("\n" + "="*60)
    print("TESTING LATEST TVPI VALUE")
    print("="*60)

    df = await sheets_service.get_fund_metrics()

    print(f"\n📊 Total rows: {len(df)}")
    print(f"\n📅 First row (oldest):")
    print(f"   Time: {df.iloc[0]['Time']}")
    print(f"   TVPI: {df.iloc[0]['RV TVPI']}")

    print(f"\n📅 Last row (latest/current):")
    print(f"   Time: {df.iloc[-1]['Time']}")
    print(f"   TVPI: {df.iloc[-1]['RV TVPI']}")

    print(f"\n🔍 All time periods:")
    for i, row in df.iterrows():
        print(f"   {row['Time']}: TVPI = {row['RV TVPI']}")

    print(f"\n🤖 Testing data_processor.process_fund_metric():")
    result = data_processor.process_fund_metric(df, "TVPI", "latest")
    print(f"   Result: {result}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_latest_tvpi())
