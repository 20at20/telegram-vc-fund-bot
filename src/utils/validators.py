"""
Input validation utilities.
"""

from typing import List

from config.settings import settings


def is_authorized_user(user_id: int) -> bool:
    """
    Check if a Telegram user ID is authorized to use the bot.

    Args:
        user_id: Telegram user ID

    Returns:
        True if authorized, False otherwise
    """
    return user_id in settings.allowed_telegram_ids


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: User input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Truncate to max length
    text = text[:max_length]

    # Remove any potentially harmful characters
    # (This is basic sanitization; adjust based on your needs)
    text = text.strip()

    return text


def validate_sheet_range(range_string: str) -> bool:
    """
    Validate a Google Sheets range string.

    Args:
        range_string: Range string (e.g., "Sheet1!A1:Z100")

    Returns:
        True if valid, False otherwise
    """
    try:
        if "!" not in range_string:
            return False

        sheet_name, cell_range = range_string.split("!", 1)
        if not sheet_name or not cell_range:
            return False

        # Basic validation of cell range format
        if ":" not in cell_range:
            return False

        return True
    except Exception:
        return False
