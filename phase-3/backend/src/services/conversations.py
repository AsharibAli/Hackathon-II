"""
Service for managing conversation and message persistence.
"""
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select

from models.conversation import Conversation
from models.message import Message


def get_or_create_conversation(session: Session, user_id: UUID) -> Conversation:
    """
    Get the existing conversation for a user or create a new one.
    MVP: Only one active conversation per user.
    """
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation


def get_recent_messages(session: Session, conversation_id: UUID, limit: int = 50) -> List[Message]:
    """
    Get recent messages for a conversation, ordered chronologically.
    """
    # Get messages ordered by creation time descending (newest first)
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()
    
    # Reverse to chronological order (oldest first)
    return messages[::-1]


def store_message(session: Session, conversation_id: UUID, role: str, content: str) -> Message:
    """
    Store a new message in the conversation and update timestamp.
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        session.add(conversation)

    session.commit()
    session.refresh(message)
    return message
