# OS, utilities, logging, dotenv
import os
import logging
import pprint

# telegram.ext
from telegram import Update
from telegram.ext import ContextTypes, ContextTypes


# TLDR Bot
from db.db import get_db, add_update_to_database, ensure_database_schema


# Handler for archiving group chats
async def archive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log the update
    logging.info(f"Received update: {update}")

    # Add the update to the database
    ensure_database_schema()

    with next(get_db()) as session:
        add_update_to_database(update.to_dict(), session.bind)