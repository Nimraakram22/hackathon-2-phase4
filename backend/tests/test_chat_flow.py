#!/usr/bin/env python3
"""Test the complete chat flow with user context."""

import asyncio
import json
from uuid import uuid4

from src.agent.todo_agent import todo_agent
from src.agent.session import get_agent_session
from agents import Runner


async def test_chat_flow():
    """Test that user_id is properly passed through the system."""

    # Simulate a user
    user_id = str(uuid4())
    conversation_id = uuid4()

    print(f"Testing with user_id: {user_id}")
    print(f"Conversation ID: {conversation_id}")
    print("-" * 80)

    # Get agent session
    agent_session = get_agent_session(user_id, conversation_id)

    # Create context with user_id (this is what the chatkit route does)
    context = {"user_id": user_id}

    # Test message
    user_message = "hi! list my todos"

    print(f"\nUser: {user_message}")
    print("\nRunning agent...")

    try:
        # Run agent with context
        result = await Runner.run(
            todo_agent,
            user_message,
            session=agent_session,
            context=context,
        )

        # Get response
        agent_response = result.final_output if hasattr(result, 'final_output') else str(result)

        print(f"\nAgent response:")
        print(agent_response)
        print("\n" + "-" * 80)

        # Check if agent is asking for user_id (which would be wrong)
        if "user id" in agent_response.lower() or "user_id" in agent_response.lower():
            print("❌ FAIL: Agent is still asking for user_id!")
            print("   This means the context is not being passed correctly.")
            return False
        else:
            print("✅ PASS: Agent is not asking for user_id")
            print("   Context is being passed correctly!")
            return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_chat_flow())
    exit(0 if success else 1)
