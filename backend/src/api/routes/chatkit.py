"""
ChatKit routes for conversation management.

This module provides endpoints for ChatKit integration with thread and message management.
"""

import logging
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from agents import Runner

from src.database.connection import get_session
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.api.dependencies import get_current_user
from src.agent.todo_agent import todo_agent
from src.agent.session import get_agent_session, get_session_id, validate_session_id
from src.agent.session_manager import SessionManager
from src.api.thread_queue import thread_queue
from src.config import settings

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/chatkit", tags=["chatkit"])


class CreateThreadRequest(BaseModel):
    """Request to create a new conversation thread."""

    title: Optional[str] = Field(None, max_length=200, description="Optional thread title")


class CreateThreadResponse(BaseModel):
    """Response with created thread information."""

    thread_id: UUID
    title: Optional[str]
    created_at: str


class SendMessageRequest(BaseModel):
    """Request to send a message to a thread."""

    text: str = Field(..., min_length=1, max_length=2000, description="User message content")


@router.post("/threads", response_model=CreateThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    request: CreateThreadRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> CreateThreadResponse:
    """
    Create a new conversation thread.

    Creates a new conversation thread for the authenticated user. Threads are used to
    maintain conversation context across multiple messages with the AI agent.

    Args:
        request: Thread creation request with optional title
        current_user: Authenticated user (injected from JWT token)
        session: Database session (injected)

    Returns:
        CreateThreadResponse: Created thread information with ID and timestamps

    Raises:
        HTTPException: 401 Unauthorized if authentication fails

    Example:
        ```bash
        curl -X POST http://localhost:8001/chatkit/threads \\
          -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"title": "My Todo List"}'
        ```
    """
    conversation = Conversation(
        user_id=current_user.id,
        title=request.title,
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return CreateThreadResponse(
        thread_id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
    )


@router.post("/threads/{thread_id}/messages")
async def send_message(
    thread_id: UUID,
    request: SendMessageRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> StreamingResponse:
    """
    Send a message to a conversation thread and stream AI agent response.

    Sends a user message to the specified thread and streams the AI agent's response
    using Server-Sent Events (SSE). The agent processes the message using available
    MCP tools for task management and maintains conversation context via SQLiteSession.

    The agent can perform the following operations through natural language:
    - Create tasks: "Add a task to buy groceries"
    - List tasks: "Show me my tasks", "What's pending?"
    - Complete tasks: "Mark task 3 as done"
    - Update tasks: "Change task 1 to 'Buy milk and eggs'"
    - Delete tasks: "Delete the groceries task"

    Args:
        thread_id: Conversation thread UUID
        request: Message request with text content (1-2000 characters)
        current_user: Authenticated user (injected from JWT token)
        session: Database session (injected)

    Returns:
        StreamingResponse: Server-Sent Events stream with agent response chunks

    Raises:
        HTTPException: 404 Not Found if thread doesn't exist or doesn't belong to user
        HTTPException: 401 Unauthorized if authentication fails
        HTTPException: 400 Bad Request if message validation fails

    Example:
        ```bash
        curl -X POST http://localhost:8001/chatkit/threads/THREAD_ID/messages \\
          -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"text": "Add a task to buy groceries"}'
        ```

    Note:
        - Messages are validated by input guardrails to ensure they're task-related
        - Non-task-related messages will be blocked with an explanation
        - Conversation context is maintained across messages within the same thread
        - The first message in a thread auto-generates the thread title
        - Concurrent requests to the same thread are processed sequentially (FR-012)
    """
    # Acquire thread lock for sequential processing (FR-012)
    thread_lock = await thread_queue.acquire_thread_lock(thread_id)

    async with thread_lock:
        logger.debug(f"Processing message for thread {thread_id}, user {current_user.id}")

        # Verify thread exists and belongs to user
        conversation = session.query(Conversation).filter(
            Conversation.id == thread_id,
            Conversation.user_id == current_user.id,
            Conversation.is_deleted == False,
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found or does not belong to user",
            )

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.text,
        )
        session.add(user_message)

        # Update conversation title from first message if not set
        if not conversation.title and request.text:
            conversation.title = request.text[:50] + ("..." if len(request.text) > 50 else "")

        session.commit()

        # Get agent session for conversation context
        agent_session = get_agent_session(current_user.id, conversation.id)

        # Validate session ID format (FR-014, T023)
        session_id = get_session_id(current_user.id, conversation.id)
        if not validate_session_id(session_id):
            logger.error(f"Invalid session ID generated: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create valid session",
            )

        # Log session isolation (T024)
        logger.info(f"Session isolation: user={current_user.id}, conversation={conversation.id}, session={session_id}")

        # Initialize session manager for pruning
        session_manager = SessionManager(
            db_path=settings.agent_session_db_path,
            max_messages=settings.agent_session_max_messages,
            retention_days=settings.agent_session_retention_days,
        )

        # Run agent with user message
        async def generate_response():
            """Generate streaming response from agent."""
            import json
            import sqlite3

            warning_message = None

            try:
                # Create context with user_id for tools
                context = {"user_id": str(current_user.id)}

                # Run agent with session context and user context (FR-007: database unavailable handling)
                try:
                    result = await Runner.run(
                        todo_agent,
                        request.text,
                        session=agent_session,
                        context=context,
                    )
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as db_error:
                    # Database unavailable - continue without context (FR-007)
                    logger.error(f"Session database unavailable: {db_error}")
                    warning_message = "Context unavailable - continuing without conversation history"

                    # Run without session
                    result = await Runner.run(
                        todo_agent,
                        request.text,
                        context=context,
                    )
                except (json.JSONDecodeError, ValueError) as data_error:
                    # Corrupted session data - clear and retry (FR-013, T038)
                    logger.error(f"Corrupted session data detected: {data_error}")
                    warning_message = "Session data corrupted - starting fresh conversation"

                    try:
                        await session_manager.clear_session(session_id)
                        logger.info(f"Cleared corrupted session {session_id}")
                    except Exception as clear_error:
                        logger.error(f"Failed to clear corrupted session: {clear_error}")

                    # Retry with cleared session
                    result = await Runner.run(
                        todo_agent,
                        request.text,
                        session=agent_session,
                        context=context,
                    )

                # Get agent response
                agent_response = result.final_output if hasattr(result, 'final_output') else str(result)

                # Save assistant message
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=agent_response,
                )
                session.add(assistant_message)
                session.commit()

                # Prune session messages if over limit (FR-010)
                try:
                    deleted_count = await session_manager.prune_session_messages(session_id)
                    if deleted_count > 0:
                        logger.info(f"Pruned {deleted_count} messages from session {session_id}")
                except Exception as prune_error:
                    # Log but don't fail the request if pruning fails
                    logger.error(f"Failed to prune session {session_id}: {prune_error}")

                # Stream response as SSE in JSON format with optional warning (T040)
                response_data = {'content': agent_response}
                if warning_message:
                    response_data['warning'] = warning_message

                yield f"data: {json.dumps(response_data)}\n\n"

            except Exception as e:
                error_message = f"Error processing message: {str(e)}"
                logger.error(f"Error in send_message for thread {thread_id}: {e}")
                # Send error in JSON format
                yield f"data: {json.dumps({'error': error_message})}\n\n"

        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
        )


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    limit: int = 50,
) -> dict:
    """
    Get conversation thread details with message history.

    Retrieves a conversation thread with its complete message history, including both
    user messages and AI agent responses. Messages are returned in chronological order.

    Args:
        thread_id: Conversation thread UUID
        current_user: Authenticated user (injected from JWT token)
        session: Database session (injected)
        limit: Maximum number of messages to return (default: 50, max: 50)

    Returns:
        dict: Thread information with messages array containing:
            - thread_id: Thread UUID
            - title: Thread title (auto-generated from first message)
            - created_at: Thread creation timestamp
            - updated_at: Last message timestamp
            - messages: Array of message objects with id, role, content, created_at

    Raises:
        HTTPException: 404 Not Found if thread doesn't exist or doesn't belong to user
        HTTPException: 401 Unauthorized if authentication fails

    Example:
        ```bash
        curl -X GET http://localhost:8001/chatkit/threads/THREAD_ID?limit=50 \\
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
        ```

    Note:
        - Messages are ordered chronologically (oldest first)
        - Deleted threads (is_deleted=True) are not accessible
        - Use limit parameter for pagination of long conversations
    """
    conversation = session.query(Conversation).filter(
        Conversation.id == thread_id,
        Conversation.user_id == current_user.id,
        Conversation.is_deleted == False,
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found or does not belong to user",
        )

    # Get messages for conversation
    messages = session.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).limit(limit).all()

    return {
        "thread_id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "message_id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
    }
