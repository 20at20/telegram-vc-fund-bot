#!/usr/bin/env python3
"""
Test complete flow for company count query.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets_service import sheets_service
from src.services.data_processor import data_processor
from src.services.query_analyzer import query_analyzer
from src.services.response_generator import response_generator


async def test_complete_flow():
    """Test complete query flow."""
    print("\n" + "="*60)
    print("TESTING COMPLETE FLOW: Company Count Query")
    print("="*60)

    query = "how many companies in portfolio?"
    print(f"\n📝 User Query: {query}")

    # Step 1: Analyze query
    intent = await query_analyzer.analyze(query, None)
    print(f"\n🔍 Step 1: Intent Analysis")
    print(f"   Query type: {intent.query_type}")
    print(f"   Filters: {intent.filters}")

    # Step 2: Fetch data
    fund_df = await sheets_service.get_fund_metrics()
    portfolio_df = await sheets_service.get_portfolio_data()
    print(f"\n📊 Step 2: Data Fetched")
    print(f"   Portfolio rows (raw): {len(portfolio_df)}")

    # Step 3: Process data
    processed_data = data_processor.process_query(intent, fund_df, portfolio_df)
    print(f"\n⚙️  Step 3: Data Processed")
    if hasattr(processed_data, '__len__'):
        print(f"   Result rows: {len(processed_data)}")
        if hasattr(processed_data, 'columns'):
            print(f"   Result columns: {list(processed_data.columns)[:3]}...")

    # Step 4: Generate response
    response = await response_generator.generate(processed_data, query, None)
    print(f"\n💬 Step 4: Generated Response")
    print(f"   {response}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
