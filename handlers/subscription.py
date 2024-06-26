from telegram import Update
from telegram.ext import CallbackContext
from sqlalchemy.orm import Session
from sqlmodel import select
from db.db import get_db, ensure_database_schema
from db.models import Subscriber

async def subscribe_user(update: Update, context: CallbackContext):
    ensure_database_schema()
    user = update.effective_user
    user_id = user.id
    username = user.username

    db_session = next(get_db())

    with db_session as session:
        # Check if the user is already subscribed
        statement = select(Subscriber).where(Subscriber.user_id == user_id)
        existing_subscriber = session.execute(statement).scalars().first()

        if existing_subscriber:
            # Reply
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are already subscribed.")
        else:
            # Add the user to the Subscriber table
            subscriber = Subscriber(user_id=user_id, username=username)
            session.add(subscriber)
            session.commit()

            # Reply
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You have successfully subscribed to daily TLDRs.")

async def unsubscribe_user(update: Update, context: CallbackContext):
    ensure_database_schema()
    user = update.effective_user
    user_id = user.id

    db_session = next(get_db())

    with db_session as session:
        # Check if the user is subscribed
        statement = select(Subscriber).where(Subscriber.user_id == user_id)
        existing_subscriber = session.execute(statement).scalars().first()

        if existing_subscriber:
            # Remove the user from the Subscriber table
            session.delete(existing_subscriber)
            session.commit()

            # Reply
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You have successfully unsubscribed from the daily TLDRs.")
        else:
            # Reply
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not subscribed.")
