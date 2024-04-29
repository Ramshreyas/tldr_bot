# TLDR bot
from templates.scripts import HELP_SCRIPT, UNKNOWN_COMMAND_SCRIPT


# telegram.ext
from telegram import Update
from telegram.ext import ContextTypes, ContextTypes


# Handler for /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_SCRIPT)


# Handler for direct chats
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_SCRIPT)


# Handler for unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=UNKNOWN_COMMAND_SCRIPT)