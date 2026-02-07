#!/usr/bin/env python3
"""
Test script to verify all API connections are working.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


def print_test(name, status, message=""):
    """Print a formatted test result."""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}: {message}")


async def test_telegram():
    """Test Telegram bot connection."""
    try:
        import httpx

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

            if data.get("ok"):
                bot_info = data.get("result", {})
                bot_name = bot_info.get("username", "Unknown")
                print_test("Telegram Bot", True, f"Connected as @{bot_name}")
                return True
            else:
                print_test("Telegram Bot", False, "Invalid token")
                return False

    except Exception as e:
        print_test("Telegram Bot", False, str(e))
        return False


async def test_openai():
    """Test OpenAI API connection."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Simple test request
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5,
        )

        if response.choices:
            print_test("OpenAI API", True, f"Model: {settings.openai_model}")
            return True
        else:
            print_test("OpenAI API", False, "No response from API")
            return False

    except Exception as e:
        error_msg = str(e)
        if "model" in error_msg.lower():
            print_test(
                "OpenAI API",
                False,
                f"Model access issue. Try 'gpt-3.5-turbo' instead of '{settings.openai_model}'",
            )
        else:
            print_test("OpenAI API", False, error_msg)
        return False


async def test_google_sheets():
    """Test Google Sheets connection."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        # Load credentials
        credentials = Credentials.from_service_account_file(
            settings.google_credentials_file, scopes=scopes
        )

        # Initialize client
        client = gspread.authorize(credentials)

        # Test fund metrics sheet
        try:
            sheet = client.open_by_key(settings.fund_metrics_sheet_id)
            print_test(
                "Fund Metrics Sheet",
                True,
                f"Connected to '{sheet.title}'",
            )
            fund_success = True
        except Exception as e:
            print_test("Fund Metrics Sheet", False, str(e))
            fund_success = False

        # Test portfolio sheet
        try:
            sheet = client.open_by_key(settings.portfolio_sheet_id)
            print_test(
                "Portfolio Sheet",
                True,
                f"Connected to '{sheet.title}'",
            )
            portfolio_success = True
        except Exception as e:
            print_test("Portfolio Sheet", False, str(e))
            portfolio_success = False

        return fund_success and portfolio_success

    except FileNotFoundError:
        print_test(
            "Google Sheets",
            False,
            f"Credentials file not found: {settings.google_credentials_file}",
        )
        return False
    except Exception as e:
        print_test("Google Sheets", False, str(e))
        return False


async def main():
    """Run all connection tests."""
    print("\n🔍 Testing API Connections\n")
    print("="*60)

    results = []

    # Test Telegram
    print("\n📱 Testing Telegram Bot...")
    results.append(await test_telegram())

    # Test OpenAI
    print("\n🤖 Testing OpenAI API...")
    results.append(await test_openai())

    # Test Google Sheets
    print("\n📊 Testing Google Sheets Access...")
    results.append(await test_google_sheets())

    # Summary
    print("\n" + "="*60)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("\nYour bot is ready to run. Start it with:")
        print("  python src/main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the errors above before running the bot.")
        print("\nCommon fixes:")
        print("1. Check your .env file has all required variables")
        print("2. Verify Google Sheets are shared with service account")
        print("3. Ensure OpenAI API key has correct permissions")
        print("4. Verify Telegram bot token is correct")

    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
