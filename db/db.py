# General
import os
import pprint
from datetime import datetime
import logging
from typing import Optional

# SQLAlchemy
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import func

# TLDR Bot modules
from config.config import Config
from db.models import ChatType, Chat, User, Message, Update, TLDR

# PostgreSQL connection URL
DATABASE_HOST = "db"  # Service name in docker-compose.yml
DATABASE_PORT = "5432"
DATABASE_NAME = "updatesdb"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = Config.DATABASE_PASSWORD

ENGINE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(ENGINE_URL, echo=True, pool_pre_ping=True)


# Creating a sessionmaker bound to this engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_database_schema(engine=engine):
    # If schema doesn't exist, create it
    SQLModel.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_update_to_database(update_data, engine):
    # Ensure the database schema exists
    ensure_database_schema(engine)
    
    with Session(engine) as session:
        # Deconstruct the nested update_data structure
        # Chat data
        pprint.pprint(update_data)
        chat_data = update_data.get('message', update_data.get('edited_message', {})).get('chat', {})
        chat_type_data = chat_data['type']
        chat_type = ChatType(type_name=chat_type_data.value)
        chat_data['type'] = chat_type
        chat = Chat(chat_id=chat_data.pop('id'), **chat_data)

        # User data
        user_data = update_data.get('message', update_data.get('edited_message', {})).get('from', {})
        user = User(user_id=user_data.pop('id'), **user_data)

        message_data = update_data.get('message', update_data.get('edited_message', {}))
        message_data['chat'] = chat
        message_data['from_user'] = user
        message = Message(message_id = message_data.pop('message_id'), **message_data)

        # Check if reply_to_message exists
        if 'reply_to_message' in message_data:
            reply_chat_data = message_data['reply_to_message']['chat']
            reply_chat_data_type = reply_chat_data['type']
            reply_chat_type = ChatType(type_name=reply_chat_data_type.value)
            reply_chat_data['type'] = reply_chat_type
            reply_chat = Chat(chat_id = reply_chat_data.pop('id'), **reply_chat_data)

            reply_user_data = message_data['reply_to_message']['from']
            reply_user = User(user_id = reply_user_data.pop('id'), **reply_user_data)

            reply_message_data = message_data['reply_to_message']
            reply_message_data['chat'] = reply_chat
            reply_message_data['from_user'] = reply_user
            reply_message = Message(message_id = reply_message_data.pop('message_id'), **reply_message_data)
            message.reply_to_message = reply_message
            session.add(reply_message)

        pprint.pprint(message)

        session.add(message)

        update = Update(update_id=update_data['update_id'], message=message)
        session.add(update)
        session.commit()


def add_tldr_to_database(tldr: dict, engine):
    # Ensure tables are created
    SQLModel.metadata.create_all(engine)
    
    # Extract data from the dictionary
    metadata_info = tldr['metadata']
    data_info_list = tldr['data']
    
    if not isinstance(metadata_info, dict) or not isinstance(data_info_list, list):
        raise ValueError("Expected dictionary for metadata and list for data information")
    
    tldr_entry = TLDR(
        start_time=metadata_info['start_time'],
        end_time=metadata_info['end_time']
    )
    tldr_entry.set_data(data_info_list)
    
    with Session(engine) as session:
        session.add(tldr_entry)
        session.commit()
        session.refresh(tldr_entry)
    
    return tldr_entry


def get_tldr(engine, date: datetime) -> Optional[dict]:
    with Session(engine) as session:
        # Extract the date and hour part from the given datetime
        day_and_hour = date.replace(minute=0, second=0, microsecond=0)

        # Query the TLDR entry where the start_time matches the given day and hour
        statement = (
            select(TLDR)
            .where(func.to_char(TLDR.start_time, 'YYYY-MM-DD HH24') == day_and_hour.strftime('%Y-%m-%d %H'))
        )
        tldr_entry = session.exec(statement).first()

        if tldr_entry:
            # Construct the tldr dictionary
            tldr_dict = {
                "metadata": {
                    "start_time": tldr_entry.start_time,
                    "end_time": tldr_entry.end_time
                },
                "data": tldr_entry.get_data()
            }
            return tldr_dict

    return None


def reconstruct_chat_as_text(engine, start_time: datetime, end_time: datetime):
    chat_history = []
    with Session(engine) as session:
        # Define the query with a time filter and order by date
        statement = select(Message, User).join(User).where(
            (Message.date >= start_time.timestamp()) & 
            (Message.date <= end_time.timestamp())
        ).order_by(Message.date)

        results = session.exec(statement).all()

        for message, user in results:
            if message.reply_to_message_id:
                # Fetch the original message and user if the current message is a reply
                original_message = session.get(Message, message.reply_to_message_id)
                original_user = session.get(User, original_message.from_user_id)
                chat_line = f"{user.username}: <replying to: {original_user.username}: {original_message.text}> {message.text}"
            else:
                chat_line = f"{user.username}: {message.text}"
            
            chat_history.append(chat_line)

    return "\n".join(chat_history)