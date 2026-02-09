"""
Request queueing for conversation threads.

Ensures sequential processing of concurrent requests to the same thread (FR-012).
"""

import asyncio
import logging
from typing import Dict
from uuid import UUID

logger = logging.getLogger(__name__)


class ThreadRequestQueue:
    """Manages request queues for conversation threads.

    Ensures that concurrent requests to the same thread are processed
    sequentially to prevent race conditions and maintain session consistency.
    """

    def __init__(self):
        """Initialize the thread request queue manager."""
        self._locks: Dict[UUID, asyncio.Lock] = {}
        self._lock_access = asyncio.Lock()

    async def acquire_thread_lock(self, thread_id: UUID) -> asyncio.Lock:
        """
        Acquire a lock for the specified thread.

        Args:
            thread_id: Conversation thread UUID

        Returns:
            asyncio.Lock for the thread
        """
        async with self._lock_access:
            if thread_id not in self._locks:
                self._locks[thread_id] = asyncio.Lock()
                logger.debug(f"Created new lock for thread {thread_id}")

            return self._locks[thread_id]

    async def cleanup_thread_lock(self, thread_id: UUID) -> None:
        """
        Clean up lock for thread if no longer needed.

        Args:
            thread_id: Conversation thread UUID
        """
        async with self._lock_access:
            if thread_id in self._locks:
                lock = self._locks[thread_id]
                if not lock.locked():
                    del self._locks[thread_id]
                    logger.debug(f"Cleaned up lock for thread {thread_id}")


# Global thread request queue instance
thread_queue = ThreadRequestQueue()
