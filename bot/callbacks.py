from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .utils import user_languages, MESSAGES, user_topic

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = query.data.split('_')[1]
    user_languages[user_id] = language

    message = MESSAGES[language]['language_selected']
    await query.edit_message_text(text=message)

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
    user_topic[user_id] = topic
    if topic == 'housing':
        message = MESSAGES[language]['housing_info']
    elif topic == 'university':
        message = MESSAGES[language]['university_info']
    else:
        message = "Topic not found"

    await query.edit_message_text(text=message)