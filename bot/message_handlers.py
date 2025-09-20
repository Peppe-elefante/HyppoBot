from telegram import Update
from telegram.ext import ContextTypes
from .utils import message_history

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    response = handle_response(text)

    await update.message.reply_text(response)

def handle_response(text: str) -> str:
    from llm.Groq_client import GroqClient
    llm_model = GroqClient()
    response = llm_model.generate(text,message_history) 
    if len(message_history) > 1:
        message_history.pop(0)
    message_history.append((text, response))
    return response