# OS, utils
from datetime import datetime, timedelta
import logging

# telegram.ext
from telegram import Update
from telegram.ext import ContextTypes, ContextTypes

# tldr
from tldr.tldr import fetch_latest_tldr, format_tldr


# Handler for /tldr
async def tldr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log that 'tl;dr' was called
    logging.info(f"Received 'tl;dr' command from: {update.effective_user.username}")

    # Get the latest tldr
    latest_tldr = fetch_latest_tldr()

    # Send the user a message
    await context.bot.send_message(chat_id=update.effective_user.id, text=format_tldr(latest_tldr))