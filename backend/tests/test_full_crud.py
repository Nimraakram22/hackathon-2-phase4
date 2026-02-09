#!/usr/bin/env python3
"""Test the complete CRUD flow for tasks through the chatbot."""

import asyncio
import httpx
import json
from uuid import uuid4


async def test_full_crud():
    """Test creating, listing, updating, completing, and deleting tasks."""

    base_url = "http://localhost:8001"
    test_email = f"test_{uuid4().hex[:8]}@example.com"
    test_password = "testpass123"

    print(f"Testing full CRUD flow with: {test_email}")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Setup: Register and create thread
        resp = await client.post(
            f"{base_url}/auth/register",
            json={"email": test_email, "password": test_password}
        )
        token = resp.json()["access_token"]
        user_id = resp.json()["user_id"]

        resp = await client.post(
            f"{base_url}/chatkit/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )
        thread_id = resp.json()["thread_id"]

        print(f"✓ Setup complete - User: {user_id}, Thread: {thread_id}\n")

        async def send_message(message: str) -> str:
            """Send a message and return the response."""
            print(f"👤 User: {message}")

            full_response = ""
            async with client.stream(
                "POST",
                f"{base_url}/chatkit/threads/{thread_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={"text": message}
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    print(f"❌ Error: {body.decode()}")
                    return ""

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if not data or data == "[DONE]":
                            continue

                        try:
                            parsed = json.loads(data)
                            if "content" in parsed:
                                full_response += parsed["content"]
                            elif "error" in parsed:
                                print(f"❌ Error: {parsed['error']}")
                                return ""
                        except json.JSONDecodeError:
                            full_response += data

            print(f"🤖 Agent: {full_response}\n")
            return full_response

        # Test 1: Create tasks
        print("TEST 1: Creating tasks")
        print("-" * 80)

        resp1 = await send_message("Add a task to buy groceries")
        if not resp1 or "user id" in resp1.lower():
            print("❌ FAIL: Task creation failed or asking for user_id")
            return False
        print("✓ Task 1 created\n")

        resp2 = await send_message("Create a task: finish the project report")
        if not resp2 or "user id" in resp2.lower():
            print(" FAIL: Task creation failed or asking for user_id")
            return False
        print("✓ Task 2 created\n")

        resp3 = await send_message("Add task: call dentist for appointment")
        if not resp3 or "user id" in resp3.lower():
            print("❌ FAIL: Task creation failed or asking for user_id")
            return False
        print("✓ Task 3 created\n")

        # Test 2: List tasks
        print("TEST 2: Listing tasks")
        print("-" * 80)

        resp = await send_message("Show me all my tasks")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: List tasks failed or asking for user_id")
            return False

        # Check if tasks are in the response
        if "groceries" not in resp.lower() or "project" not in resp.lower():
            print("❌ FAIL: Tasks not found in list")
            return False
        print("✓ All tasks listed correctly\n")

        # Test 3: List pending tasks
        print("TEST 3: Listing pending tasks")
        print("-" * 80)

        resp = await send_message("What are my pending tasks?")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: List pending tasks failed")
            return False
        print("✓ Pending tasks listed\n")

        # Test 4: Complete a task
        print("TEST 4: Completing a task")
        print("-" * 80)

        resp = await send_message("Mark the groceries task as complete")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: Complete task failed")
            return False
        print("✓ Task completed\n")

        # Test 5: List completed tasks
        print("TEST 5: Listing completed tasks")
        print("-" * 80)

        resp = await send_message("Show me my completed tasks")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: List completed tasks failed")
            return False

        if "groceries" not in resp.lower():
            print("❌ FAIL: Completed task not found")
            return False
        print("✓ Completed tasks listed correctly\n")

        # Test 6: Update a task
        print("TEST 6: Updating a task")
        print("-" * 80)

        resp = await send_message("Change the project task to 'finish quarterly report'")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: Update task failed")
            return False
        print("✓ Task updated\n")

        # Test 7: Delete a task
        print("TEST 7: Deleting a task")
        print("-" * 80)

        resp = await send_message("Delete the dentist task")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: Delete task failed")
            return False
        print("✓ Task deleted\n")

        # Test 8: Final list to verify changes
        print("TEST 8: Final verification")
        print("-" * 80)

        resp = await send_message("List all my tasks")
        if not resp or "user id" in resp.lower():
            print("❌ FAIL: Final list failed")
            return False

        # Should have quarterly report, not dentist
        if "quarterly" not in resp.lower():
            print("❌ FAIL: Updated task not found")
            return False

        if "dentist" in resp.lower():
            print("❌ FAIL: Deleted task still appears")
            return False

        print("✓ All changes verified\n")

        print("=" * 80)
        print("✅ ALL CRUD TESTS PASSED!")
        print("=" * 80)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_full_crud())
    exit(0 if success else 1)
