# OS, utilities, logging, dotenv
import logging

# Add /app to the start of the sys.path list
import sys
sys.path.insert(0, '/app')

# Telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

# TLDR Bot
from config.config import Config
from templates.scripts import HELP_SCRIPT, UNKNOWN_COMMAND_SCRIPT
from handlers.bot_interactions import help, chat, unknown
from handlers.archiver import archive
from handlers.tldr import tldr
from handlers.subscription import subscribe_user, unsubscribe_user 


# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
    
    # Register handlers
    tldr_handler = CommandHandler('tldr', tldr)
    subscription_handler = CommandHandler('subscribe', subscribe_user)
    unsubscription_handler = CommandHandler('unsubscribe', unsubscribe_user)
    archive_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), archive)
    # chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & (~filters.ChatType.GROUP), chat)
    # help_handler = CommandHandler('help', help)
    # start_handler = CommandHandler('start', help)
    # unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers to the application
    application.add_handler(tldr_handler)
    application.add_handler(archive_handler)
    application.add_handler(subscription_handler)
    application.add_handler(unsubscription_handler)
    # application.add_handler(chat_handler)
    # application.add_handler(help_handler)
    # application.add_handler(start_handler)
    # application.add_handler(unknown_handler)
    
    application.run_polling()