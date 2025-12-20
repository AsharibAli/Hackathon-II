"""
Chat orchestration service.
Handles message processing, AI agent invocation, and response storage.
"""
from uuid import UUID
from sqlmodel import Session
from models.message import Message
from services.conversations import (
    store_message,
    get_recent_messages
)
from mcp.agent import ChatAgent

def process_user_message(session: Session, user_id: UUID, message_content: str, conversation_id: UUID) -> Message:
    """
    Process a user message: persist it, invoke AI agent, and persist response.
    """
    # 1. Store the user's message
    store_message(session, conversation_id, "user", message_content)
    
    # 2. Get conversation history for context
    recent_messages = get_recent_messages(session, conversation_id)
    history = [{"role": m.role, "content": m.content} for m in recent_messages]
    
    # 3. Initialize AI agent
    agent = ChatAgent(session, user_id)
    
    # 4. Get agent response
    response_content = agent.process_message(history)
    
    # 5. Store assistant's response
    assistant_message = store_message(session, conversation_id, "assistant", response_content)
    
    return assistant_message