"""
Chat orchestration service.
Handles message processing, AI agent invocation, and response storage.
"""
from uuid import UUID
from sqlmodel import Session
from models.message import Message
from services.conversations import (
    get_or_create_conversation,
    store_message,
    get_recent_messages
)
from mcp.agent import ChatAgent

def process_user_message(session: Session, user_id: UUID, message_content: str) -> Message:
    """
    Process a user message: persist it, invoke AI agent, and persist response.
    """
    # 1. Get or create conversation for the user
    conversation = get_or_create_conversation(session, user_id)
    
    # 2. Store the user's message
    store_message(session, conversation.id, "user", message_content)
    
    # 3. Get conversation history for context
    # Includes the message we just stored
    recent_messages = get_recent_messages(session, conversation.id)
    history = [{"role": m.role, "content": m.content} for m in recent_messages]
    
    # 4. Initialize AI agent
    agent = ChatAgent(session, user_id)
    
    # 5. Get agent response
    response_content = agent.process_message(history)
    
    # 6. Store assistant's response
    assistant_message = store_message(session, conversation.id, "assistant", response_content)
    
    return assistant_message