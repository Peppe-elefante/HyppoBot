import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
from llm.Groq_client import GroqClient
from bot.commands import start, help_command
from bot.callbacks import language_callback
from bot.message_handlers import handle_message
from rag.pipeline import RAGPipeline

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    rag = RAGPipeline("hyppo-data", "sentence-transformers/all-MiniLM-L6-v2")

    rag.add_text_files("data")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    logger.info("Starting HyppoBot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()