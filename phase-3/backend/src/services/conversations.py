"""
Service for managing conversation and message persistence.
"""
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select

from models.conversation import Conversation
from models.message import Message


def get_or_create_conversation(session: Session, user_id: UUID, conversation_id: Optional[UUID] = None) -> Conversation:
    """
    Get an existing conversation by ID, or create a new one if not provided.
    If conversation_id is provided, validates it belongs to the user.
    """
    if conversation_id:
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        ).first()
        if conversation:
            return conversation
    
    # Create new conversation if ID not provided or not found
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def list_conversations(session: Session, user_id: UUID) -> List[Conversation]:
    """
    Get all conversations for a user, ordered by most recently updated.
    """
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()
    return list(conversations)


def get_conversation_by_id(session: Session, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
    """
    Get a specific conversation by ID, ensuring it belongs to the user.
    """
    return session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    ).first()


def create_conversation(session: Session, user_id: UUID, title: Optional[str] = None) -> Conversation:
    """
    Create a new conversation for a user.
    """
    conversation = Conversation(user_id=user_id, title=title)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def rename_conversation(session: Session, conversation_id: UUID, user_id: UUID, new_title: str) -> Optional[Conversation]:
    """
    Rename an existing conversation. Returns None if not found or not owned by user.
    """
    conversation = get_conversation_by_id(session, conversation_id, user_id)
    if not conversation:
        return None
    
    conversation.title = new_title
    conversation.updated_at = datetime.now(timezone.utc)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def delete_conversation(session: Session, conversation_id: UUID, user_id: UUID) -> bool:
    """
    Delete a conversation and all its messages. Returns True if deleted, False if not found.
    """
    conversation = get_conversation_by_id(session, conversation_id, user_id)
    if not conversation:
        return False
    
    session.delete(conversation)
    session.commit()
    return True


def update_conversation_title(session: Session, conversation_id: UUID, title: str) -> None:
    """
    Update the title of a conversation (used for auto-titling from first message).
    """
    conversation = session.get(Conversation, conversation_id)
    if conversation and not conversation.title:
        conversation.title = title[:100]  # Limit to max length
        session.add(conversation)
        session.commit()


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
    return list(messages[::-1])


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
