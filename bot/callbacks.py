from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .utils import user_languages, MESSAGES

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = query.data.split('_')[1]
    user_languages[user_id] = language

    message = MESSAGES[language]['language_selected']
    await query.edit_message_text(text=message)

