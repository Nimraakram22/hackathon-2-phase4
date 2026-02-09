"""
Database cleanup utilities.

This module provides utilities for cleaning up old conversations and maintaining data retention policies.
It also manages the background cleanup job for inactive agent sessions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from ..config import settings
from ..database.connection import get_session_context
from ..models.conversation import Conversation
from ..agent.session_manager import SessionManager

logger = logging.getLogger(__name__)


def mark_old_conversations_for_deletion() -> int:
    """
    Mark conversations older than retention period for deletion.

    Returns:
        Number of conversations marked for deletion
    """
    retention_days = settings.conversation_retention_days
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    with get_session_context() as session:
        # Mark conversations as deleted if they haven't been updated in retention_days
        result = session.query(Conversation).filter(
            Conversation.updated_at < cutoff_date,
            Conversation.is_deleted == False,
        ).update({
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
        })

        return result


def purge_deleted_conversations() -> int:
    """
    Permanently delete conversations that have been marked deleted for 30 days.

    Returns:
        Number of conversations permanently deleted
    """
    purge_cutoff = datetime.utcnow() - timedelta(days=30)

    with get_session_context() as session:
        # Find conversations to purge
        conversations_to_purge = session.query(Conversation).filter(
            Conversation.is_deleted == True,
            Conversation.deleted_at < purge_cutoff,
        ).all()

        count = len(conversations_to_purge)

        # Delete conversations (cascade will delete messages)
        for conversation in conversations_to_purge:
            session.delete(conversation)

        return count


class SessionCleanupJob:
    """Manages background cleanup job for inactive agent sessions."""

    def __init__(self):
        """Initialize session cleanup job."""
        self.cleanup_task = None
        self.is_running = False

    async def start(self):
        """Start the background cleanup job."""
        if self.is_running:
            logger.warning("Session cleanup job already running")
            return

        self.is_running = True
        logger.info("Starting session cleanup job")

        # Create cleanup task
        self.cleanup_task = asyncio.create_task(self._run_cleanup_loop())

    async def stop(self):
        """Stop the background cleanup job."""
        if not self.is_running:
            return

        self.is_running = False
        logger.info("Stopping session cleanup job")

        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                logger.info("Session cleanup job cancelled successfully")

    async def _run_cleanup_loop(self):
        """Run cleanup job in a loop."""
        while self.is_running:
            try:
                # Wait until configured cleanup hour
                await self._wait_until_cleanup_time()

                if not self.is_running:
                    break

                # Run cleanup
                await self._run_cleanup()

                # Wait 24 hours before next cleanup
                await asyncio.sleep(24 * 60 * 60)

            except asyncio.CancelledError:
                logger.info("Session cleanup loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in session cleanup loop: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(60 * 60)

    async def _wait_until_cleanup_time(self):
        """Wait until the configured cleanup hour."""
        now = datetime.utcnow()
        target_hour = settings.agent_session_cleanup_hour

        # Calculate seconds until target hour
        if now.hour < target_hour:
            # Target hour is today
            target_time = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        else:
            # Target hour is tomorrow
            tomorrow = now + timedelta(days=1)
            target_time = tomorrow.replace(hour=target_hour, minute=0, second=0, microsecond=0)

        wait_seconds = (target_time - now).total_seconds()

        if wait_seconds > 0:
            logger.info(f"Waiting {wait_seconds / 3600:.1f} hours until next cleanup at {target_time} UTC")
            await asyncio.sleep(wait_seconds)

    async def _run_cleanup(self):
        """Run the cleanup job."""
        start_time = datetime.utcnow()
        logger.info(f"Starting session cleanup at {start_time} UTC")

        try:
            # Initialize session manager
            manager = SessionManager(
                db_path=settings.agent_session_db_path,
                max_messages=settings.agent_session_max_messages,
                retention_days=settings.agent_session_retention_days,
            )

            # Run cleanup
            deleted_count = await manager.cleanup_inactive_sessions()

            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Log results (T031)
            logger.info(
                f"Session cleanup completed: deleted={deleted_count}, "
                f"duration={duration:.2f}s, timestamp={end_time}"
            )

            # Log metrics for monitoring (T031)
            logger.info(f"METRIC: session_cleanup_deleted_count={deleted_count}")
            logger.info(f"METRIC: session_cleanup_duration_seconds={duration:.2f}")
            logger.info(f"METRIC: session_cleanup_success=1")

        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
            logger.info("METRIC: session_cleanup_success=0")
            raise


# Global session cleanup job instance
session_cleanup_job = SessionCleanupJob()

