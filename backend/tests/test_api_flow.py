#!/usr/bin/env python3
"""Test the complete API flow including SSE streaming."""

import asyncio
import httpx
import json
from uuid import uuid4


async def test_api_flow():
    """Test the complete API flow with SSE streaming."""

    base_url = "http://localhost:8001"

    # Create a unique test user
    test_email = f"test_{uuid4().hex[:8]}@example.com"
    test_password = "testpass123"

    print(f"Testing with email: {test_email}")
    print("-" * 80)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register user
        print("\n1. Registering user...")
        resp = await client.post(
            f"{base_url}/auth/register",
            json={"email": test_email, "password": test_password}
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code != 201:
            print(f"   Error: {resp.text}")
            return False

        user_data = resp.json()
        token = user_data["access_token"]
        user_id = user_data["user_id"]
        print(f"   ✓ User ID: {user_id}")
        print(f"   ✓ Token: {token[:20]}...")

        # 2. Create thread
        print("\n2. Creating conversation thread...")
        resp = await client.post(
            f"{base_url}/chatkit/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code != 201:
            print(f"   Error: {resp.text}")
            return False

        thread_data = resp.json()
        thread_id = thread_data["thread_id"]
        print(f"   ✓ Thread ID: {thread_id}")

        # 3. Send message and test SSE streaming
        print("\n3. Sending message and testing SSE stream...")
        message = "hi! list my todos"
        print(f"   Message: '{message}'")

        async with client.stream(
            "POST",
            f"{base_url}/chatkit/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={"text": message}
        ) as resp:
            print(f"   Status: {resp.status_code}")
            print(f"   Content-Type: {resp.headers.get('content-type')}")

            if resp.status_code != 200:
                body = await resp.aread()
                print(f"   Error: {body.decode()}")
                return False

            print("\n   SSE Stream:")
            full_response = ""
            chunk_count = 0

            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    chunk_count += 1
                    data = line[6:].strip()

                    if not data or data == "[DONE]":
                        continue

                    print(f"   Chunk {chunk_count}: {data[:100]}...")

                    try:
                        parsed = json.loads(data)
                        if "content" in parsed:
                            full_response += parsed["content"]
                        elif "error" in parsed:
                            print(f"   ❌ Error in response: {parsed['error']}")
                            return False
                    except json.JSONDecodeError as e:
                        print(f"   ⚠ JSON parse error: {e}")
                        print(f"   Raw data: {data}")
                        # Treat as plain text
                        full_response += data

            print(f"\n   Total chunks received: {chunk_count}")
            print(f"\n   Full response:")
            print(f"   {full_response}")

            # Check if response is valid
            if not full_response:
                print("\n   ❌ FAIL: No response received!")
                return False

            if "user id" in full_response.lower() or "what is your user id" in full_response.lower():
                print("\n   ❌ FAIL: Agent is asking for user_id!")
                print("   This means the context is not being passed correctly.")
                return False

            print("\n   ✓ Response received successfully!")
            print("   ✓ Agent is not asking for user_id")

        # 4. Verify message was saved
        print("\n4. Verifying messages were saved...")
        resp = await client.get(
            f"{base_url}/chatkit/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   Status: {resp.status_code}")

        if resp.status_code == 200:
            thread_data = resp.json()
            messages = thread_data.get("messages", [])
            print(f"   ✓ Found {len(messages)} messages")

            for msg in messages:
                print(f"   - {msg['role']}: {msg['content'][:50]}...")

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_api_flow())
    exit(0 if success else 1)
