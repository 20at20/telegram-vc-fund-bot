"""
News service — fetches Google News RSS for each portfolio company daily.
Results are cached in memory and refreshed by APScheduler.
"""

import asyncio
import calendar
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

import feedparser
import httpx

from src.services.sheets_service import sheets_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── In-memory cache ────────────────────────────────────────────────────────────

_news_cache: list = []   # list of {"name": str, "news": list[dict]}
_last_refreshed: str = ""


# ── Date parsing ───────────────────────────────────────────────────────────────

def _parse_date(entry) -> datetime | None:
    """Parse publish date from a feedparser entry. Returns UTC-aware datetime or None."""
    try:
        if getattr(entry, "published_parsed", None):
            return datetime.fromtimestamp(
                calendar.timegm(entry.published_parsed), tz=timezone.utc
            )
    except Exception:
        pass

    try:
        raw = getattr(entry, "published", None)
        if raw:
            import email.utils
            return email.utils.parsedate_to_datetime(raw)
    except Exception:
        pass

    return None


# ── Per-company fetch ──────────────────────────────────────────────────────────

def _is_empty(value: str) -> bool:
    return value.lower() in ("", "nan", "n/a", "none", "-")


async def _fetch_company_news(company: dict) -> list[dict]:
    """
    Fetch Google News RSS for a company.
    Query: "{name}" startup {vertical} {region}
    Returns up to 2 items published within the last 7 days.
    Returns [] on any error or timeout.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    name = company["name"]
    parts = [f'"{name}"', "startup"]
    if not _is_empty(company.get("vertical", "")):
        parts.append(company["vertical"])
    if not _is_empty(company.get("country", "")):
        parts.append(company["country"])
    query = " ".join(parts)

    url = (
        f"https://news.google.com/rss/search"
        f"?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
    )

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
    except Exception as e:
        logger.warning("HTTP error fetching news", company=name, error=str(e))
        return []

    try:
        feed = feedparser.parse(content)
    except Exception as e:
        logger.warning("feedparser error", company=name, error=str(e))
        return []

    results: list[dict] = []
    for entry in feed.entries[:10]:  # inspect up to 10, keep first 2 that qualify
        pub_date = _parse_date(entry)
        if pub_date is None:
            continue
        if pub_date < cutoff:
            continue

        raw_snippet = getattr(entry, "summary", "")
        snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()[:220]

        results.append({
            "title": getattr(entry, "title", "").strip(),
            "link": getattr(entry, "link", "").strip(),
            "published": pub_date.strftime("%b %d, %Y"),
            "snippet": snippet,
        })

        if len(results) == 2:
            break

    return results


# ── Company data loader ────────────────────────────────────────────────────────

async def _get_company_data() -> list[dict]:
    """
    Read portfolio companies from the Portfolio sheet.
    Filters to RV portfolio only ("Is RV portfolio?" == "Yes").
    Returns list of {name, vertical, country} dicts.
    """
    try:
        df = await sheets_service.get_portfolio_data()
        if df.empty:
            logger.warning("Portfolio sheet returned empty data")
            return []

        # Filter to RV portfolio companies only
        rv_col = next(
            (c for c in df.columns if "rv portfolio" in c.lower()),
            None,
        )
        if rv_col:
            df = df[df[rv_col].astype(str).str.strip().str.lower() == "yes"]

        first_col = df.columns[0]

        vertical_col = next(
            (c for c in df.columns if any(k in c.lower() for k in ("vertical", "sector"))),
            None,
        )
        # Prefer country/region-level column over city-level HQ
        country_col = next(
            (c for c in df.columns if "country" in c.lower()),
            None,
        ) or next(
            (c for c in df.columns if "region" in c.lower()),
            None,
        ) or next(
            (c for c in df.columns if any(k in c.lower() for k in ("hq", "location"))),
            None,
        )

        companies = []
        for _, row in df.iterrows():
            name = str(row[first_col]).strip()
            if not name or _is_empty(name):
                continue
            vertical = str(row[vertical_col]).strip() if vertical_col else ""
            country = str(row[country_col]).strip() if country_col else ""
            companies.append({"name": name, "vertical": vertical, "country": country})

        logger.info(
            "Portfolio companies loaded for news",
            count=len(companies),
            all_cols=list(df.columns),
            vertical_col=vertical_col,
            country_col=country_col,
        )
        return companies

    except Exception as e:
        logger.error("Failed to load portfolio company data", error=str(e))
        return []


# ── Scheduler-triggered refresh ────────────────────────────────────────────────

async def refresh_all_news() -> None:
    """
    Fetch news for all portfolio companies and update the in-memory cache.
    Called on startup and once daily by APScheduler.
    """
    global _news_cache, _last_refreshed

    logger.info("News refresh started")
    companies = await _get_company_data()

    if not companies:
        logger.warning("No portfolio companies found — skipping news refresh")
        return

    sem = asyncio.Semaphore(5)  # max 5 concurrent Google News requests

    async def fetch_with_semaphore(company: dict) -> tuple[str, list[dict]]:
        async with sem:
            news = await _fetch_company_news(company)
            return company["name"], news

    results = await asyncio.gather(
        *[fetch_with_semaphore(c) for c in companies],
        return_exceptions=True,
    )

    new_cache: list[dict] = []
    companies_with_news = 0

    for result in results:
        if isinstance(result, Exception):
            logger.warning("Unexpected error fetching company news", error=str(result))
            continue
        name, news = result
        if news:
            new_cache.append({"name": name, "news": news})
            companies_with_news += 1

    _news_cache = new_cache
    _last_refreshed = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    logger.info(
        "News refresh complete",
        total_companies=len(companies),
        companies_with_news=companies_with_news,
    )


# ── Accessor (called by the API endpoint) ─────────────────────────────────────

def get_cached_news() -> dict:
    """Return the cached news data synchronously (no I/O)."""
    return {
        "companies": _news_cache,
        "last_refreshed": _last_refreshed,
        "total": len(_news_cache),
    }
