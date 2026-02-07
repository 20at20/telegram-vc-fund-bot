"""
Bot middleware for authorization and rate limiting.
"""

import time
from collections import defaultdict
from typing import Dict

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings
from src.utils.logger import get_logger
from src.utils.validators import is_authorized_user

logger = get_logger(__name__)


class RateLimiter:
    """Simple rate limiter to prevent abuse."""

    def __init__(self, max_requests: int = 20, time_window: int = 3600):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds (default: 1 hour)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[int, list] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if a user is allowed to make a request.

        Args:
            user_id: Telegram user ID

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()

        # Remove old requests outside the time window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.time_window
        ]

        # Check if under limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True

        return False

    def get_remaining_requests(self, user_id: int) -> int:
        """Get number of remaining requests for a user."""
        now = time.time()
        recent_requests = [
            req_time for req_time in self.requests.get(user_id, [])
            if now - req_time < self.time_window
        ]
        return max(0, self.max_requests - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_per_user,
    time_window=3600,  # 1 hour
)


async def authorization_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user is authorized to use the bot.

    Returns:
        True if authorized, False otherwise
    """
    if not update.effective_user:
        return False

    user_id = update.effective_user.id
    username = update.effective_user.username

    # Check authorization
    if not is_authorized_user(user_id):
        logger.warning(
            "Unauthorized access attempt",
            user_id=user_id,
            username=username,
        )

        if update.message:
            await update.message.reply_text(
                "❌ You are not authorized to use this bot. "
                "Please contact your fund administrator for access."
            )

        return False

    logger.debug("User authorized", user_id=user_id, username=username)
    return True


async def rate_limit_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user is within rate limits.

    Returns:
        True if allowed, False if rate limited
    """
    if not update.effective_user:
        return False

    user_id = update.effective_user.id

    if not rate_limiter.is_allowed(user_id):
        remaining = rate_limiter.get_remaining_requests(user_id)

        logger.warning("Rate limit exceeded", user_id=user_id)

        if update.message:
            await update.message.reply_text(
                f"⏱ You've reached the rate limit of {settings.rate_limit_per_user} requests per hour. "
                "Please try again later."
            )

        return False

    return True
