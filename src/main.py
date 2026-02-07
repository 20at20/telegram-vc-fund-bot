"""
Main entry point for the Telegram VC Fund Metrics Bot.
"""

import asyncio
import signal
import sys

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import settings
from src.bot.handlers import (
    start_command,
    help_command,
    clear_command,
    handle_message,
    error_handler,
)
from src.bot.middleware import authorization_middleware, rate_limit_middleware
from src.services.mcp_client import mcp_client
from src.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


class BotApplication:
    """Main bot application class."""

    def __init__(self):
        """Initialize the bot application."""
        self.application = None
        self.shutdown_event = asyncio.Event()

    async def initialize(self):
        """Initialize the bot and all services."""
        logger.info("Initializing VC Fund Metrics Bot...")

        # Initialize MCP client
        await mcp_client.connect()

        # Create Telegram application
        self.application = (
            Application.builder()
            .token(settings.telegram_bot_token)
            .build()
        )

        # Register command handlers
        self.application.add_handler(CommandHandler("start", self._with_middleware(start_command)))
        self.application.add_handler(CommandHandler("help", self._with_middleware(help_command)))
        self.application.add_handler(CommandHandler("clear", self._with_middleware(clear_command)))

        # Register message handler (for queries)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self._with_middleware(handle_message),
            )
        )

        # Register error handler
        self.application.add_error_handler(error_handler)

        logger.info("Bot initialized successfully")

    def _with_middleware(self, handler):
        """
        Wrap a handler with middleware checks.

        Args:
            handler: The handler function to wrap

        Returns:
            Wrapped handler function
        """
        async def wrapped_handler(update, context):
            # Check authorization
            if not await authorization_middleware(update, context):
                return

            # Check rate limiting
            if not await rate_limit_middleware(update, context):
                return

            # Call the actual handler
            await handler(update, context)

        return wrapped_handler

    async def start(self):
        """Start the bot."""
        logger.info("Starting bot...")

        # Initialize the bot
        await self.application.initialize()
        await self.application.start()

        # Start polling for updates
        await self.application.updater.start_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
        )

        logger.info("✅ Bot started successfully and is now polling for messages")
        logger.info(f"Authorized users: {settings.allowed_telegram_ids}")

        # Wait for shutdown signal
        await self.shutdown_event.wait()

    async def stop(self):
        """Stop the bot gracefully."""
        logger.info("Stopping bot...")

        if self.application:
            # Stop receiving updates
            await self.application.updater.stop()

            # Stop the application
            await self.application.stop()
            await self.application.shutdown()

        # Disconnect MCP client
        await mcp_client.disconnect()

        logger.info("Bot stopped successfully")

    def signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        self.shutdown_event.set()


async def main():
    """Main function to run the bot."""
    bot = BotApplication()

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, bot.signal_handler)
    signal.signal(signal.SIGTERM, bot.signal_handler)

    try:
        # Initialize and start the bot
        await bot.initialize()
        await bot.start()

    except Exception as e:
        logger.error("Fatal error in bot", error=str(e), exc_info=True)
        sys.exit(1)

    finally:
        # Ensure clean shutdown
        await bot.stop()


if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        sys.exit(1)
