"""
Chat API endpoints.
Handles chat interaction with the AI assistant.
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
from models.conversation import Conversation
from services.chat import process_user_message
from services.conversations import (
    get_or_create_conversation,
    get_recent_messages,
    update_conversation_title,
    get_conversation_by_id
)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message content")
    conversation_id: Optional[str] = Field(None, description="Conversation ID (creates new if not provided)")

class ChatResponse(BaseModel):
    message: Message
    conversation_id: str

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    messages: List[Message]
    updated_at: str

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to the AI assistant",
    description="Process user message and return AI response."
)
async def chat(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> ChatResponse:
    """
    Send a message to the AI assistant.
    The system will:
    1. Get or create conversation
    2. Store your message
    3. Invoke the AI agent with available tools
    4. Store and return the AI's response
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        # Parse conversation_id if provided
        conv_uuid = None
        if request.conversation_id:
            try:
                conv_uuid = UUID(request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )

        # Get or create conversation
        conversation = get_or_create_conversation(session, current_user.id, conv_uuid)
        
        # Check if this is the first message (for auto-titling)
        existing_messages = get_recent_messages(session, conversation.id, limit=1)
        is_first_message = len(existing_messages) == 0
        
        # Process the message
        response_message = process_user_message(session, current_user.id, request.message, conversation.id)
        
        # Auto-title the conversation if this is the first message
        if is_first_message:
            # Use first 50 characters of message as title
            auto_title = request.message[:50].strip()
            if len(request.message) > 50:
                auto_title += "..."
            update_conversation_title(session, conversation.id, auto_title)
        
        return ChatResponse(
            message=response_message,
            conversation_id=str(conversation.id)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/conversations",
    response_model=ConversationResponse,
    summary="Get conversation history",
    description="Get the active conversation and its history."
)
async def get_conversation(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    conversation_id: Optional[str] = None
) -> ConversationResponse:
    """
    Retrieve a conversation's history.
    If conversation_id is not provided, returns the most recent conversation.
    """
    conv_uuid = None
    if conversation_id:
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )
    
    conversation = get_or_create_conversation(session, current_user.id, conv_uuid)
    messages = get_recent_messages(session, conversation.id)
    
    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        messages=messages,
        updated_at=conversation.updated_at.isoformat()
    )
