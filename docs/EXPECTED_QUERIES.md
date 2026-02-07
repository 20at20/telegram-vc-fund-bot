# Expected User Queries - VC Fund Metrics Bot

## Fund-Level Calculations

### Investment Metrics
- "What's our average check size?"
- "What's the average investment amount?"
- "What's our median investment?"
- "What's our largest investment?"
- "What's our smallest investment?"
- "Total invested capital?"
- "How much have we invested in total?"

### Return Metrics
- "What's our average return?"
- "What's the median return across portfolio?"
- "Average MOIC?" (Multiple on Invested Capital)
- "What's our best performing investment?"
- "What's our worst performing investment?"

### Portfolio Composition
- "How many companies by stage?" (breakdown)
- "How many companies by sector/vertical?"
- "How many companies by region?"
- "Portfolio distribution by stage"
- "Portfolio distribution by geography"

### Performance Over Time
- "What was our IRR last quarter?"
- "TVPI trend over time"
- "DPI history"
- "How has our portfolio value changed?"

### Exit Metrics
- "How many exits do we have?"
- "What's our exit rate?"
- "Average time to exit?"
- "Total realized value?"

## Portfolio-Level Queries

### Company Rankings
- "Top 5 companies by return"
- "Top 5 by investment amount"
- "Worst performers"
- "Best performers"
- "Most recent investments"

### Filtering & Search
- "Show all fintech companies"
- "Show Series A investments"
- "Show European companies"
- "Companies invested in 2024"

### Company Details
- "Tell me about Deel"
- "When did we invest in Discord?"
- "What stage is Alma at?"
- "What's the valuation of Pipe?"

## Comparison Queries
- "Compare Deel and Discord"
- "How does our FinTech portfolio compare to HealthTech?"
- "Best performing sector?"
- "Which region has highest returns?"

## Implementation Notes

### Already Supported ✅
- Fund metrics: TVPI, DPI, IRR (latest value)
- Time series: trends over time
- Portfolio ranking: top/bottom N by any metric
- Portfolio list: filtering by sector/stage/region
- Company details: specific company information
- Company count: number of portfolio companies

### Need to Add ✅
1. **Aggregation calculations**:
   - Average, median, sum, min, max
   - For: investment amount, return, valuation

2. **Distribution/breakdown queries**:
   - Count by stage, sector, region
   - Portfolio composition analytics

3. **Comparison queries**:
   - Compare two companies
   - Compare two sectors/regions

4. **Derived metrics**:
   - Exit rate (exits / total companies)
   - Average time to exit
   - Concentration metrics (top 5 as % of total)

### Query Type Mapping

| Query Pattern | Query Type | Processing Method |
|--------------|-----------|------------------|
| "Average check size" | `portfolio_aggregation` | `process_portfolio_aggregation()` |
| "Total invested" | `portfolio_aggregation` | `process_portfolio_aggregation()` |
| "Companies by sector" | `portfolio_distribution` | `process_portfolio_distribution()` |
| "Best performing sector" | `portfolio_distribution` | `process_portfolio_distribution()` |
| "Compare X and Y" | `portfolio_comparison` | `process_portfolio_comparison()` |
