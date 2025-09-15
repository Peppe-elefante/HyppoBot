import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from llm.ollama_client import OllamaClient

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

user_languages = {}

MESSAGES = {
    'en': {
        'welcome': 'Welcome to HyppoBot!\n\nPlease select your preferred language:',
        'language_selected': 'Language set to English!',
        'topic_selection': 'What topics do you want to know about?',
        'help': 'This is the help message in English.',
        'housing_info': 'What would you like to Know about housing in Salerno?',
        'university_info': 'What would you like to know about university in Salerno?'
    },
    'es': {
        'welcome': 'Bienvenido a HyppoBot!\n\nPor favor selecciona tu idioma preferido:',
        'language_selected': 'Idioma configurado en Espanol!',
        'topic_selection': 'Que temas quieres conocer?',
        'help': 'Este es el mensaje de ayuda en Espanol.',
        'housing_info': '¿Qué te gustaría saber sobre vivienda en Salerno?',
        'university_info': '¿Qué te gustaría saber sobre la universidad en Salerno?'
    }
}

message_history = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
            InlineKeyboardButton("Espanol", callback_data="lang_es"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to HyppoBot! / Bienvenido a HyppoBot!\n\nPlease select your language / Selecciona tu idioma:",
        reply_markup=reply_markup
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = query.data.split('_')[1]
    user_languages[user_id] = language

    message = MESSAGES[language]['language_selected']
    await query.edit_message_text(text=message)

    # Show topic selection
    keyboard = [
        [
            InlineKeyboardButton("Housing" if language == 'en' else "Vivienda", callback_data="topic_housing"),
            InlineKeyboardButton("University" if language == 'en' else "Universidad", callback_data="topic_university"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    topic_message = MESSAGES[language]['topic_selection']
    await query.message.reply_text(topic_message, reply_markup=reply_markup)

async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = user_languages.get(user_id, 'en')
    topic = query.data.split('_')[1]

    if topic == 'housing':
        message = MESSAGES[language]['housing_info']
    elif topic == 'university':
        message = MESSAGES[language]['university_info']
    else:
        message = "Topic not found"

    await query.edit_message_text(text=message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    language = user_languages.get(user_id, 'en')

    message = MESSAGES[language]['help']
    await update.message.reply_text(message)

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(topic_callback, pattern="^topic_"))

    logger.info("Starting HyppoBot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()