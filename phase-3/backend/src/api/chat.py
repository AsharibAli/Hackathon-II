"""
Chat API endpoints.
Handles chat interaction with the AI assistant.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import Annotated, List
from pydantic import BaseModel, Field

from core.database import get_session
from api.dependencies import get_current_user
from models.user import User
from models.message import Message
from models.conversation import Conversation
from services.chat import process_user_message
from services.conversations import get_or_create_conversation, get_recent_messages

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message content")

class ChatResponse(BaseModel):
    message: Message

class ConversationResponse(BaseModel):
    id: str
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
    1. Store your message
    2. Invoke the AI agent with available tools
    3. Store and return the AI's response
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        response_message = process_user_message(session, current_user.id, request.message)
        return ChatResponse(message=response_message)
    except Exception as e:
        # In a real app, log the full error
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
    session: Annotated[Session, Depends(get_session)]
) -> ConversationResponse:
    """
    Retrieve the current user's active conversation history.
    """
    conversation = get_or_create_conversation(session, current_user.id)
    messages = get_recent_messages(session, conversation.id)
    
    return ConversationResponse(
        id=str(conversation.id),
        messages=messages,
        updated_at=conversation.updated_at.isoformat()
    )
