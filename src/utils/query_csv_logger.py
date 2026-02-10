"""
CSV logger for user queries. Appends one row per query to a CSV file.
"""

import csv
import os
from datetime import datetime
from pathlib import Path

CSV_PATH = Path(os.environ.get("DATA_DIR", "/data")) / "query_log.csv"

HEADERS = ["timestamp", "user_id", "username", "query", "query_type", "metric", "company", "success"]


def log_query_to_csv(user_id, username, query, intent=None, success=True):
    """Append a query record to the CSV file."""
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    write_header = not CSV_PATH.exists()

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "username": username or "",
            "query": query,
            "query_type": getattr(intent, "query_type", "") if intent else "",
            "metric": getattr(intent, "metric", "") if intent else "",
            "company": getattr(intent, "company_name", "") if intent else "",
            "success": success,
        })
