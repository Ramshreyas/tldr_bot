# OS, utilities, logging, dotenv
import os
import logging
import pprint
import dotenv
dotenv.load_dotenv()


# Telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes


# TLDR Bot
from config.config import Config
from templates.scripts import HELP_SCRIPT, UNKNOWN_COMMAND_SCRIPT
from handlers.bot_interactions import help, chat, unknown
from handlers.archiver import archive


# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
    
    # Register handlers
    archive_handler = MessageHandler(filters.ChatType.GROUP, archive)
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & (~filters.ChatType.GROUP), chat)
    help_handler = CommandHandler('help', help)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers to the application
    application.add_handler(archive_handler)
    application.add_handler(chat_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()