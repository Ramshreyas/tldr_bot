# OS, utils
from datetime import datetime, timedelta

# telegram.ext
from telegram import Update
from telegram.ext import ContextTypes, ContextTypes

# tldr_bot
from config.config import Config
import db.models
from db.db import get_db, reconstruct_chat_as_text

# OpenAI
from openai import OpenAI

client = OpenAI(api_key=Config.OPENAI_API_KEY)


# Extract the main topics from a chat
def extract_topics_from_chat(chat_text):
    # Using the chat-specific completion API
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # Use an appropriate model, like 'gpt-3.5-turbo'
        messages=[{"role": "system", "content": "Please extract the general topics discussed in the following group chat:"},
                  {"role": "user", "content": chat_text}],
        max_tokens=300,
        temperature=0.1,
        stop=["\n\n"]
    )
    
    return response.choices[0].message.content


# Handler for /tldr
async def tldr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Start and End times
    previous_day = datetime.now() - timedelta(days=2)
    # Set start_time to the beginning of the previous day (00:00:00)
    start_time = datetime(previous_day.year, previous_day.month, previous_day.day, 0, 0, 0)
    # Set end_time to the end of the previous day (23:59:59)
    end_time = datetime(previous_day.year, previous_day.month, previous_day.day, 23, 59, 59)

    # Get the chat history
    with next(get_db()) as session:
        # Get the chat history
        chat_history = reconstruct_chat_as_text(session.bind, start_time, end_time)

        # Extract the topics
        topics = extract_topics_from_chat(chat_history)


        await context.bot.send_message(chat_id=update.effective_chat.id, text=topics)

