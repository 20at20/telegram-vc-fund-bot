"""
Market news service — scrapes the latest Scaling Europe newsletter issue
weekly, extracts the top funding/M&A/news items via OpenAI, and caches
the result in memory for the front-page Market News ticker.
"""

import re
from datetime import datetime, timezone
from html import unescape
from json import loads
from urllib.parse import urljoin

import httpx
from openai import AsyncOpenAI

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

NEWSLETTER_BASE_URL = "https://scaling-europe.beehiiv.com/"
_MAX_ITEMS = 10

_client = AsyncOpenAI(api_key=settings.openai_api_key)

# ── In-memory cache ─────────────────────────────────────────────────────────
# Kept on any refresh failure (scrape or extraction error) rather than
# cleared, since refresh only runs weekly — a transient failure shouldn't
# blank the widget for a week.
_items_cache: list[dict] = []
_last_refreshed: str = ""
_source_url: str = ""


async def _fetch(url: str) -> str:
    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def _find_latest_post_url(homepage_html: str) -> str | None:
    """Beehiiv lists posts newest-first, so the first /p/... link is latest."""
    match = re.search(r'href="(/p/[a-z0-9-]+)"', homepage_html, re.IGNORECASE)
    if not match:
        return None
    return urljoin(NEWSLETTER_BASE_URL, match.group(1))


def _html_to_text_with_links(html: str, base_url: str) -> str:
    """
    Strip an HTML page down to plain text, while preserving each hyperlink's
    target as an inline "[LINK: url]" marker immediately after its anchor
    text — so a later text-only extraction pass can still attribute the
    correct source link to each newsletter item.
    """
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)

    def _replace_anchor(match: re.Match) -> str:
        href = urljoin(base_url, match.group(1))
        inner_text = re.sub(r"<[^>]+>", "", match.group(2))
        return f" {inner_text} [LINK: {href}] "

    text = re.sub(
        r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        _replace_anchor,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


_EXTRACTION_SYSTEM_PROMPT = f"""You are given the plain-text content of a European tech newsletter issue.
Extract the {_MAX_ITEMS} most significant items overall — combining funding rounds, M&A, fund closes, and other big news — ranked most significant first (by deal/valuation size or importance).

For each item, find the nearest "[LINK: url]" marker that follows its description in the text and use that as its link. If no such marker follows it, use an empty string for link.

Return strict JSON: {{"items": [{{"category": "Big Round" | "M&A" | "Fund Close" | "News", "company": "...", "description": "one sentence, include amount/valuation if mentioned", "link": "..."}}]}}
Return at most {_MAX_ITEMS} items. Do not invent items, amounts, or links that aren't in the text."""


async def _extract_top_items(text: str) -> list[dict]:
    response = await _client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    parsed = loads(response.choices[0].message.content)
    items = parsed.get("items", [])
    if not isinstance(items, list):
        raise ValueError("OpenAI extraction did not return a list of items")
    return items[:_MAX_ITEMS]


async def refresh_market_news() -> None:
    """Scrape the latest newsletter issue and refresh the cache. Called on
    startup and weekly by APScheduler. Leaves the cache untouched on failure."""
    global _items_cache, _last_refreshed, _source_url

    logger.info("Market news refresh started")
    try:
        homepage_html = await _fetch(NEWSLETTER_BASE_URL)
        post_url = _find_latest_post_url(homepage_html)
        if not post_url:
            logger.warning("No newsletter post link found on homepage — skipping refresh")
            return

        post_html = await _fetch(post_url)
        text = _html_to_text_with_links(post_html, post_url)
        items = await _extract_top_items(text)

        if not items:
            logger.warning("OpenAI extraction returned no items — skipping refresh")
            return

        _items_cache = items
        _last_refreshed = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _source_url = post_url

        logger.info("Market news refresh complete", source_url=post_url, item_count=len(items))
    except Exception as e:
        logger.error("Market news refresh failed — keeping previous cache", error=str(e), exc_info=True)


def get_cached_market_news() -> dict:
    """Return the cached market news data synchronously (no I/O)."""
    return {
        "items": _items_cache,
        "last_refreshed": _last_refreshed,
        "source_url": _source_url,
    }
