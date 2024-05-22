from typing import Optional, List
from datetime import datetime
import json
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, BigInteger

class ChatType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_name: Optional[str] = Field(sa_column_kwargs={"unique": False})

class Chat(SQLModel, table=True):
    id: int = Field(primary_key=True)
    chat_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger()))
    all_members_are_administrators: Optional[bool] = Field()
    title: Optional[str] = Field()
    type_id: Optional[int] = Field(foreign_key="chattype.id")
    type: ChatType = Relationship()

class User(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    user_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger()))  # Telegram user ID
    first_name: str = Field()
    last_name: Optional[str] = Field(default=None)
    is_bot: bool = Field()
    language_code: Optional[str] = Field(default=None)
    username: Optional[str] = Field()

class Message(SQLModel, table=True):
    id: int = Field(primary_key=True)
    message_id: int = Field(default=None)
    channel_chat_created: Optional[bool] = Field()
    chat_id: int = Field(foreign_key="chat.id")
    chat: Chat = Relationship()
    date: int = Field()
    delete_chat_photo: Optional[bool] = Field()
    from_user_id: int = Field(foreign_key="user.id")
    from_user: User = Relationship()
    group_chat_created: Optional[bool] = Field()
    reply_to_message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    reply_to_message: 'Message' = Relationship(sa_relationship_kwargs={"remote_side": "Message.id"})
    supergroup_chat_created: Optional[bool] = Field()
    text: Optional[str] = Field()

class Update(SQLModel, table=True):
    update_id: int = Field(primary_key=True)
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    message: Optional[Message] = Relationship()

class TLDR(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime = Field(index=True)
    end_time: datetime
    data: str  # JSON string representation of the list of data objects

    def get_data(self) -> List[dict]:
        return json.loads(self.data)

    def set_data(self, data_list: List[dict]):
        self.data = json.dumps(data_list)

class Subscriber(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    username: str