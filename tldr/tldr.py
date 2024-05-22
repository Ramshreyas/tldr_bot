# General Imports
import os
from datetime import datetime, timedelta
from typing import List, Optional

# TLDR bot
from config.config import Config
from db.models import Message
from db.db import get_db, get_tldr, add_tldr_to_database

# SQLAlchemy & SQLModel
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

# Instantiate OpenAI chat client
from openai import OpenAI
gpt = OpenAI(api_key=Config.OPENAI_API_KEY)


# Select the conversation for a message
def select_conversation_for_message(conversations: List[List[Message]], message: Message, gpt) -> int:
    # Prompt template
    prompt = """
This is a list of indexed conversations:

{conversations}

This is a message that needs to be placed in one of the conversations above:

{message}

Please reply with the index of the conversation that the message belongs to.
Think about the context of the conversation and how the message fits in.
Your response will be converted into an int for further processing, so please 
reply with only the number and absolutely nothing else.
"""

    conversation_text = ""

    for index, conversation in enumerate(conversations):
        # Generate the conversation text with an index
        conversation_text = conversation_text + f"\n{index}: \n" + "\n".join([f"{message.from_user.username}: {message.text}" for message in conversation])

    prompt = prompt.format(conversations=conversation_text, message=f"{message.from_user.username}: {message.text}")

    # Generate the completion
    completion = gpt.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # Extract the completion choice
    choice = int(completion.choices[0].message.content.strip())

    # # Return the choice if it is valid
    if 0 <= choice < len(conversations):
        return choice
        
    return None


# Select the conversation for a message and add it to the conversation
def select_conversation_for_message_and_add(conversations: List[List[Message]], message: Message, gpt):
    # Check if the message is a direct reply
    if hasattr(message, 'reply_to_message_id') and message.reply_to_message_id:
        for conversation in conversations:
            for msg in conversation:
                if msg.id == message.reply_to_message_id:
                    conversation.append(message)
                    return
    
    # Use AI to find the right conversation for non-reply messages
    if len(conversations) > 0:
        conversation_index = select_conversation_for_message(conversations, message, gpt)
        if conversation_index is not None:
            conversations[conversation_index].append(message)
            return

    # If no conversation fits or list is empty, start a new conversation
    conversations.append([message])


# Reconstruct chat as conversations
def reconstruct_chat_as_conversations(engine, start_time: datetime, end_time: datetime, gpt) -> List[List[Message]]:
    conversations = []  # This will store lists of messages categorized into conversations
    with Session(engine) as session:
        # Fetch all messages within the given time range, ordering by the date
        statement = select(Message).where(
            Message.date >= start_time.timestamp(),  # Assuming 'date' is stored as a UNIX timestamp
            Message.date <= end_time.timestamp()
        ).order_by(Message.date)
        results = session.exec(statement).all()

        for message in results:
            select_conversation_for_message_and_add(conversations, message, gpt)
    
    return conversations


# Create transcripts from conversations
def create_transcripts_from_conversations(conversations: List[List[Message]], engine) -> str:
    transcripts = []
    
    # Create a single session to handle all operations
    with Session(engine) as session:
        for conversation in conversations:
            transcript = ""
            for message in conversation:
                # Eager load the from_user relationship
                message = session.query(Message).options(joinedload(Message.from_user)).filter(Message.id == message.id).first()
                
                # Check if the message is a reply
                if message.reply_to_message_id:
                    # Fetch the message being replied to
                    result = session.query(Message).options(joinedload(Message.from_user)).filter(Message.id == message.reply_to_message_id).first()
                    transcript += f"{message.from_user.username} (replying to {result.from_user.username}): {message.text}\n"
                else:
                    transcript += f"{message.from_user.username}: {message.text}\n"
            transcripts.append(transcript)
    
    return transcripts


# Summarize a chat
def summarize_chat(chat_text, gpt):
    # Using the chat-specific completion API
    response = gpt.chat.completions.create(
        model="gpt-4-turbo",  # Use an appropriate model, like 'gpt-3.5-turbo'
        messages=[{"role": "system", "content": """
Provide a detailed summary of the chat transcript below.
The summary should capture the key points and essence of the conversation.
When summarizing, ensure you reference the participants by name.
Finish with a conclusion that encapsulates the overall theme of the chat.
"""},
                  {"role": "user", "content": chat_text}],
        max_tokens=4096,
        temperature=0.1,
        stop=["\n\n"]
    )
    
    return response.choices[0].message.content


# Generate a title for the summery
def title_for_summary(chat_text, gpt):
    # Using the chat-specific completion API
    response = gpt.chat.completions.create(
        model="gpt-3.5-turbo",  # Use an appropriate model, like 'gpt-3.5-turbo'
        messages=[{"role": "system", "content": """
Create a short one-line title for the summary provided below.
"""},
                  {"role": "user", "content": chat_text}],
        max_tokens=250,
        temperature=0.1,
        stop=["\n\n"]
    )
    
    return response.choices[0].message.content


# Generate TLDR and save it
def generate_tldr_and_save(engine, start_time: datetime, end_time: datetime, gpt):
    # Reconstruct chat as conversations
    conversations = reconstruct_chat_as_conversations(engine, start_time, end_time, gpt)
    
    # Create transcripts from conversations
    transcripts = create_transcripts_from_conversations(conversations, engine)
    
    # Summarize each transcript
    tldr = {"metadata": {"start_time": start_time, "end_time": end_time}, "data": []}
    for transcript in transcripts:
        summary = summarize_chat(transcript, gpt)
        title = title_for_summary(summary, gpt)
        tldr["data"].append({"title": title, "summary": summary, "transcript": transcript})

    # Add the TLDR to the database
    tldr_entry = add_tldr_to_database(tldr, engine)

    return tldr


# Get latest tldr
def fetch_latest_tldr():
    # Get the previous day's date
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    # Get the database session
    with next(get_db()) as session:
        # Get the TLDR for yesterday
        tldr = get_tldr(session.bind, start_date)

        # If no TLDR exists for yesterday, generate the latest TLDR
        if not tldr:
            tldr = generate_tldr_and_save(session.bind, start_date, end_date, gpt)

    return tldr


# Format the tldr
def format_tldr(tldr):
    # Format the TLDR start date into a readable string
    formatted_tldr = f"{tldr['metadata']['start_time'].strftime('%B %d, %Y')}\n\n"

    for chat in tldr["data"]:
        formatted_tldr += f"{chat['title']}:\n\n"
        formatted_tldr += f"{chat['summary']}\n\n"
        formatted_tldr += f"---\n\n"

    return formatted_tldr