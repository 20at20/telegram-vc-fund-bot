"""
Telegram bot command and message handlers.
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.services.memory_service import memory_service
from src.services.sheets_service import sheets_service
from src.services.query_analyzer import query_analyzer
from src.services.data_processor import data_processor
from src.services.response_generator import response_generator
from src.utils.logger import get_logger
from src.utils.validators import sanitize_input
from src.utils.query_csv_logger import log_query_to_csv

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    user = update.effective_user
    user_id = user.id

    logger.info("Start command received", user_id=user_id, username=user.username)

    welcome_message = f"""
👋 *Welcome to the VC Fund Metrics Bot!*

I can help you query fund performance metrics and portfolio information.

*Example queries:*
• "What's our current TVPI?"
• "Show me top 5 companies in the portfolio"
• "List all fintech companies"
• "What's the fund's DPI?"

*Available commands:*
/help - Show this help message
/clear - Clear conversation history

Just ask me a question and I'll do my best to help!
    """

    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    user_id = update.effective_user.id
    logger.info("Help command received", user_id=user_id)

    help_message = """
*VC Fund Metrics Bot - Help*

*Query Types You Can Ask:*

📊 *Fund Metrics*
• "What's our current TVPI?"
• "Show me the latest IRR"
• "What's the DPI this quarter?"

🏢 *Portfolio Rankings*
• "Top 5 companies by investment amount"
• "Show me the top 10 companies"

📋 *Portfolio Lists*
• "List all fintech companies"
• "Show companies in Series A stage"
• "What companies are in healthcare?"

🔍 *Company Details*
• "Tell me about [Company Name]"
• "Show details for [Company Name]"

*Commands:*
/start - Start the bot
/help - Show this help
/clear - Clear conversation history

*Tips:*
• I remember your last 5 messages for context
• You can ask follow-up questions
• Use /clear if you want to start fresh
    """

    await update.message.reply_text(help_message, parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /clear command."""
    user_id = update.effective_user.id

    await memory_service.clear_history(user_id)

    logger.info("Cleared conversation history", user_id=user_id)

    await update.message.reply_text(
        "✅ Conversation history cleared! Starting fresh.",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages (queries)."""
    user = update.effective_user
    user_id = user.id
    user_question = update.message.text

    logger.info(
        "Processing user query",
        user_id=user_id,
        username=user.username,
        query=user_question,
    )

    intent = None
    success = True
    try:
        # Sanitize input
        user_question = sanitize_input(user_question)

        # Send typing indicator
        await update.message.chat.send_action("typing")

        # Step 1: Retrieve conversation history
        conversation_history = await memory_service.get_conversation_history(user_id)

        # Step 2: Analyze query intent
        intent = await query_analyzer.analyze(user_question, conversation_history)

        logger.debug("Query analyzed", user_id=user_id, intent=intent.query_type)

        # Step 3: Handle based on query type
        if intent.query_type == "general_chat":
            # For general chat, just use OpenAI directly
            response = await response_generator.generate(
                None, user_question, conversation_history
            )
        else:
            # Fetch relevant data from Google Sheets
            fund_df = await sheets_service.get_fund_metrics()
            portfolio_df = await sheets_service.get_portfolio_data()

            # Process data based on intent
            processed_data = data_processor.process_query(intent, fund_df, portfolio_df)

            # Generate response
            response = await response_generator.generate(
                processed_data, user_question, conversation_history
            )

        # Step 6: Store conversation in memory
        await memory_service.store_message(user_id, "user", user_question)
        await memory_service.store_message(user_id, "assistant", response)

        # Step 7: Send response to user
        await update.message.reply_text(response, parse_mode="Markdown")

        logger.info("Query processed successfully", user_id=user_id)

    except Exception as e:
        success = False
        logger.error("Error handling message", user_id=user_id, error=str(e), exc_info=True)

        error_message = (
            "Sorry, I encountered an error processing your request. "
            "Please try again or use /help for examples."
        )
        await update.message.reply_text(error_message)
    finally:
        log_query_to_csv(user_id, user.username, user_question, intent, success)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot."""
    logger.error("Error in bot", error=str(context.error), exc_info=context.error)

    # Notify user if possible
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Please try again later."
        )
