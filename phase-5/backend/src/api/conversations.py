"""
Conversations API endpoints.
Handles CRUD operations for conversation management.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID

from core.database import get_session
from api.dependencies import get_current_user
from models.user import User
from models.message import Message
from services.conversations import (
    list_conversations,
    get_conversation_by_id,
    create_conversation,
    rename_conversation,
    delete_conversation,
    get_recent_messages
)

router = APIRouter()


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: str
    title: Optional[str]
    updated_at: str

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Full conversation with messages."""
    id: str
    title: Optional[str]
    messages: List[Message]
    updated_at: str


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    title: Optional[str] = Field(None, max_length=100, description="Optional conversation title")


class RenameConversationRequest(BaseModel):
    """Request to rename a conversation."""
    title: str = Field(..., min_length=1, max_length=100, description="New conversation title")


@router.get(
    "",
    response_model=List[ConversationSummary],
    summary="List all conversations",
    description="Get all conversations for the current user, ordered by most recently updated."
)
async def list_user_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> List[ConversationSummary]:
    """Get all conversations for the authenticated user."""
    conversations = list_conversations(session, current_user.id)
    return [
        ConversationSummary(
            id=str(conv.id),
            title=conv.title,
            updated_at=conv.updated_at.isoformat()
        )
        for conv in conversations
    ]


@router.post(
    "",
    response_model=ConversationSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Create a new conversation with optional title."
)
async def create_new_conversation(
    request: CreateConversationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> ConversationSummary:
    """Create a new conversation."""
    conversation = create_conversation(session, current_user.id, request.title)
    return ConversationSummary(
        id=str(conversation.id),
        title=conversation.title,
        updated_at=conversation.updated_at.isoformat()
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
    summary="Get a conversation",
    description="Get a specific conversation with all its messages."
)
async def get_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> ConversationDetail:
    """Get a specific conversation with its messages."""
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    
    conversation = get_conversation_by_id(session, conv_uuid, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = get_recent_messages(session, conversation.id)
    return ConversationDetail(
        id=str(conversation.id),
        title=conversation.title,
        messages=messages,
        updated_at=conversation.updated_at.isoformat()
    )


@router.put(
    "/{conversation_id}",
    response_model=ConversationSummary,
    summary="Rename a conversation",
    description="Update the title of an existing conversation."
)
async def rename_existing_conversation(
    conversation_id: str,
    request: RenameConversationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> ConversationSummary:
    """Rename an existing conversation."""
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    
    conversation = rename_conversation(session, conv_uuid, current_user.id, request.title)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationSummary(
        id=str(conversation.id),
        title=conversation.title,
        updated_at=conversation.updated_at.isoformat()
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Delete a conversation and all its messages."
)
async def delete_existing_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> None:
    """Delete a conversation."""
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    
    deleted = delete_conversation(session, conv_uuid, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
