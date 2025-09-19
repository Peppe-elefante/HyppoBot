from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .utils import user_languages, MESSAGES

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    language = user_languages.get(user_id, 'en')

    message = MESSAGES[language]['help']
    await update.message.reply_text(message)