#!/usr/bin/env python3
"""
Test script for time series queries.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor


async def test_time_series():
    """Test time series processing."""
    print("\n" + "="*60)
    print("TESTING TIME SERIES FUNCTIONALITY")
    print("="*60)

    df = await sheets_service.get_fund_metrics()

    print(f"\n📊 Total rows: {len(df)}")
    print(f"📋 Columns: {list(df.columns)}")

    # Test DPI time series
    print(f"\n🔍 Testing DPI time series...")
    result = data_processor.process_time_series(df, "DPI")

    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Success!")
        print(f"   Metric: {result['metric']}")
        print(f"   Column: {result['metric_column']}")
        print(f"   Data points: {result['data_points']}")
        print(f"\n   Time series data:")
        for item in result['time_series']:
            print(f"      {item['period']}: {item['value']}")

    # Test TVPI time series
    print(f"\n🔍 Testing TVPI time series...")
    result = data_processor.process_time_series(df, "TVPI")

    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Success!")
        print(f"   Metric: {result['metric']}")
        print(f"   Data points: {result['data_points']}")
        print(f"\n   First 5 data points:")
        for item in result['time_series'][:5]:
            print(f"      {item['period']}: {item['value']}")
        if len(result['time_series']) > 5:
            print(f"      ... and {len(result['time_series']) - 5} more")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_time_series())
