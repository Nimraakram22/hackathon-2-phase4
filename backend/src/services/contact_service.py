"""
Contact Service
Business logic for contact form submissions
"""
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from src.models.contact_submission import (
    ContactSubmission,
    ContactSubmissionCreate,
    ContactSubmissionUpdate,
    SubmissionStatus
)


class ContactService:
    """Service for managing contact form submissions"""

    def __init__(self, session: Session):
        self.session = session

    def create_submission(
        self,
        submission_data: ContactSubmissionCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ContactSubmission:
        """
        Create a new contact submission

        Args:
            submission_data: Contact form data
            ip_address: Submitter's IP address
            user_agent: Submitter's browser user agent

        Returns:
            Created ContactSubmission
        """
        submission = ContactSubmission(
            name=submission_data.name,
            email=submission_data.email,
            subject=submission_data.subject,
            message=submission_data.message,
            status=SubmissionStatus.NEW,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(submission)
        self.session.commit()
        self.session.refresh(submission)

        return submission

    def get_submission(self, submission_id: int) -> Optional[ContactSubmission]:
        """
        Get a contact submission by ID

        Args:
            submission_id: Submission ID

        Returns:
            ContactSubmission or None if not found
        """
        statement = select(ContactSubmission).where(ContactSubmission.id == submission_id)
        return self.session.exec(statement).first()

    def list_submissions(
        self,
        status: Optional[SubmissionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ContactSubmission]:
        """
        List contact submissions with optional filtering

        Args:
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of ContactSubmission
        """
        statement = select(ContactSubmission)

        if status:
            statement = statement.where(ContactSubmission.status == status)

        statement = statement.order_by(ContactSubmission.created_at.desc())
        statement = statement.limit(limit).offset(offset)

        return list(self.session.exec(statement).all())

    def update_submission(
        self,
        submission_id: int,
        update_data: ContactSubmissionUpdate
    ) -> Optional[ContactSubmission]:
        """
        Update a contact submission (admin only)

        Args:
            submission_id: Submission ID
            update_data: Fields to update

        Returns:
            Updated ContactSubmission or None if not found
        """
        submission = self.get_submission(submission_id)
        if not submission:
            return None

        # Update fields if provided
        if update_data.status is not None:
            submission.status = update_data.status

        if update_data.assigned_to is not None:
            submission.assigned_to = update_data.assigned_to

        if update_data.response_sent is not None:
            submission.response_sent = update_data.response_sent

        # Update timestamp
        submission.updated_at = datetime.utcnow()

        self.session.add(submission)
        self.session.commit()
        self.session.refresh(submission)

        return submission

    def count_submissions_by_status(self) -> dict:
        """
        Count submissions by status

        Returns:
            Dictionary with status counts
        """
        counts = {status.value: 0 for status in SubmissionStatus}

        for status in SubmissionStatus:
            statement = select(ContactSubmission).where(ContactSubmission.status == status)
            count = len(list(self.session.exec(statement).all()))
            counts[status.value] = count

        return counts


def get_contact_service(session: Session) -> ContactService:
    """Dependency injection for ContactService"""
    return ContactService(session)
