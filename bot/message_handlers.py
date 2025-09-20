from telegram import Update
from telegram.ext import ContextTypes
from .utils import user_topic, message_history

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    topic = user_topic.get(user_id, 'housing')

    response = handle_response(text, topic)

    await update.message.reply_text(response)

def handle_response(text: str, topic: str) -> str:
    from llm.Groq_client import GroqClient
    llm_model = GroqClient()
    response = llm_model.generate(text, topic, message_history) 
    if message_history > 4:
        message_history.pop(0)
    message_history.append((text, response))
    return response