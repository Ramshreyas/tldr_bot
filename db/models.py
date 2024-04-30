from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class ChatType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_name: str = Field(sa_column_kwargs={"unique": False})

class Chat(SQLModel, table=True):
    id: int = Field(primary_key=True)
    chat_id: Optional[int] = Field(default=None)
    all_members_are_administrators: bool = Field()
    title: str = Field()
    type_id: int = Field(foreign_key="chattype.id")
    type: ChatType = Relationship()

class User(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    user_id: Optional[int] = Field(default=None)  # Telegram user ID
    first_name: str = Field()
    last_name: Optional[str] = Field(default=None)
    is_bot: bool = Field()
    language_code: str = Field()
    username: Optional[str] = Field()

class Message(SQLModel, table=True):
    message_id: int = Field(primary_key=True)
    channel_chat_created: bool = Field()
    chat_id: int = Field(foreign_key="chat.id")
    chat: Chat = Relationship()
    date: int = Field()
    delete_chat_photo: bool = Field()
    from_user_id: int = Field(foreign_key="user.id")
    from_user: User = Relationship()
    group_chat_created: bool = Field()
    reply_to_message_id: Optional[int] = Field(default=None, foreign_key="message.message_id")
    reply_to_message: 'Message' = Relationship(sa_relationship_kwargs={"remote_side": "Message.message_id"})
    supergroup_chat_created: bool = Field()
    text: Optional[str] = Field()

class Update(SQLModel, table=True):
    update_id: int = Field(primary_key=True)
    message_id: Optional[int] = Field(default=None, foreign_key="message.message_id")
    message: Optional[Message] = Relationship()