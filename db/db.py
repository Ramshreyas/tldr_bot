from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.exc import OperationalError
from db.models import ChatType, Chat, User, Message, Update
from sqlalchemy.orm import sessionmaker
import pprint

# Creating the engine
ENGINE_URL = 'sqlite:///updates.db'
engine = create_engine(ENGINE_URL, echo=True, pool_pre_ping=True)


# Creating a sessionmaker bound to this engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_database_schema(engine=engine):
    try:
        # Attempt to fetch data from an expected table to see if schema is in place
        with Session(engine) as session:
            session.execute(select(User)).first()
    except OperationalError:
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
        chat_data = update_data['message']['chat']
        chat_type_data = chat_data['type']
        chat_type = ChatType(type_name=chat_type_data.value)
        chat_data['type'] = chat_type
        chat = Chat(chat_id=chat_data.pop('id'), **chat_data)

        pprint.pprint(update_data)
        user_data = update_data['message']['from']
        user = User(user_id=user_data.pop('id'), **user_data)

        message_data = update_data['message']
        message_data['chat'] = chat
        message_data['from_user'] = user
        message = Message(**message_data)

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
            reply_message = Message(**reply_message_data)
            message.reply_to_message = reply_message
            # session.add(reply_message)

        pprint.pprint(message)

        session.add(message)

        update = Update(update_id=update_data['update_id'], message=message)
        session.add(update)
        session.commit()