# Packages
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
import pprint
from datetime import datetime

# TLDR Bot modules
from db.models import ChatType, Chat, User, Message, Update

# PostgreSQL connection URL
DATABASE_HOST = "db"  # Service name in docker-compose.yml
DATABASE_PORT = "5432"
DATABASE_NAME = "updatesdb"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "your_password"

ENGINE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(ENGINE_URL, echo=True, pool_pre_ping=True)


# Creating a sessionmaker bound to this engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_database_schema(engine=engine):
    try:
        # Attempt to fetch data from an expected table to see if schema is in place
        with Session(engine) as session:
            session.execute(select(User)).first()
    except:
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
        pprint.pprint(update_data)
        chat_data = update_data['message']['chat']
        chat_type_data = chat_data['type']
        chat_type = ChatType(type_name=chat_type_data.value)
        chat_data['type'] = chat_type
        chat = Chat(chat_id=chat_data.pop('id'), **chat_data)

        user_data = update_data['message']['from']
        user = User(user_id=user_data.pop('id'), **user_data)

        message_data = update_data['message']
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
            # session.add(reply_message)

        pprint.pprint(message)

        session.add(message)

        update = Update(update_id=update_data['update_id'], message=message)
        session.add(update)
        session.commit()

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