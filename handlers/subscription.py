from telegram import Update
from telegram.ext import CallbackContext
from sqlmodel import Session, select
from sqlalchemy.orm import Session
from db.db import get_db
from db.models import Subscriber

def subscribe_user(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    username = user.username

    db_session = next(get_db())

    with db_session as session:
        # Check if the user is already subscribed
        statement = select(Subscriber).where(Subscriber.user_id == user_id)
        existing_subscriber = session.execute(statement).scalars().first()

        if existing_subscriber:
            update.message.reply_text("You are already subscribed.")
        else:
            # Add the user to the Subscriber table
            subscriber = Subscriber(user_id=user_id, username=username)
            session.add(subscriber)
            session.commit()
            update.message.reply_text("You have successfully subscribed to daily TLDRs.")


def unsubscribe_user(update: Update, context: CallbackContext):
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
            update.message.reply_text("You have successfully unsubscribed from daily TLDRs.")
        else:
            update.message.reply_text("You are not subscribed.")
