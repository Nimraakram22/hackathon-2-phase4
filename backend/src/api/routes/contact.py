"""
Contact API Routes
Endpoints for contact form submissions
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib

from src.api.schemas.contact import (
    ContactSubmissionCreate,
    ContactSubmissionPublic,
    ContactSubmissionUpdate,
    ContactSubmissionResponse,
    SubmissionStatus
)
from src.services.contact_service import ContactService, get_contact_service
from src.database.connection import get_session

router = APIRouter(prefix="/api/contact", tags=["contact"])

# Rate limiting: Store submission timestamps by IP hash
_rate_limit_store: dict[str, list[datetime]] = {}
RATE_LIMIT_MAX = 5  # Maximum submissions per hour per IP
RATE_LIMIT_WINDOW = timedelta(hours=1)


def check_rate_limit(ip_address: str) -> bool:
    """
    Check if IP has exceeded rate limit

    Args:
        ip_address: Client IP address

    Returns:
        True if within rate limit, False if exceeded
    """
    # Hash IP for privacy
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()

    now = datetime.utcnow()
    cutoff = now - RATE_LIMIT_WINDOW

    # Get submissions for this IP
    if ip_hash not in _rate_limit_store:
        _rate_limit_store[ip_hash] = []

    # Remove old submissions outside the window
    _rate_limit_store[ip_hash] = [
        ts for ts in _rate_limit_store[ip_hash] if ts > cutoff
    ]

    # Check if limit exceeded
    if len(_rate_limit_store[ip_hash]) >= RATE_LIMIT_MAX:
        return False

    # Add current submission
    _rate_limit_store[ip_hash].append(now)
    return True


@router.post(
    "",
    response_model=ContactSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit contact form",
    description="Create a new contact form submission with rate limiting (5 per hour per IP)"
)
async def create_contact_submission(
    submission: ContactSubmissionCreate,
    request: Request,
    session: Session = Depends(get_session)
) -> ContactSubmissionResponse:
    """
    Create a new contact form submission

    Rate limit: 5 submissions per hour per IP address
    """
    # Get client IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Check rate limit
    if ip_address and not check_rate_limit(ip_address):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 5 submissions per hour."
        )

    # Create submission
    try:
        contact_service = ContactService(session)
        created_submission = contact_service.create_submission(
            submission_data=submission,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # TODO: Send email notification to support team
        # from src.services.email_service import get_email_service
        # email_service = get_email_service()
        # await email_service.send_contact_notification(created_submission)

        return ContactSubmissionResponse(
            id=created_submission.id,
            message="Your message has been received. We'll get back to you soon.",
            created_at=created_submission.created_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create submission: {str(e)}"
        )


@router.get(
    "",
    response_model=List[ContactSubmissionPublic],
    summary="List contact submissions (Admin only)",
    description="Get all contact submissions with optional status filtering"
)
async def list_contact_submissions(
    status: Optional[SubmissionStatus] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session)
    # TODO: Add admin authentication dependency
    # current_user: User = Depends(get_current_admin_user)
) -> List[ContactSubmissionPublic]:
    """
    List all contact submissions (admin only)

    Query parameters:
    - status: Filter by submission status
    - limit: Maximum number of results (default: 100)
    - offset: Number of results to skip (default: 0)
    """
    try:
        contact_service = ContactService(session)
        submissions = contact_service.list_submissions(
            status=status,
            limit=limit,
            offset=offset
        )

        return [
            ContactSubmissionPublic.model_validate(sub)
            for sub in submissions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list submissions: {str(e)}"
        )


@router.patch(
    "/{submission_id}",
    response_model=ContactSubmissionPublic,
    summary="Update contact submission (Admin only)",
    description="Update submission status, assignment, or response flag"
)
async def update_contact_submission(
    submission_id: int,
    update_data: ContactSubmissionUpdate,
    session: Session = Depends(get_session)
    # TODO: Add admin authentication dependency
    # current_user: User = Depends(get_current_admin_user)
) -> ContactSubmissionPublic:
    """
    Update a contact submission (admin only)

    Allows updating:
    - status: Workflow status (new, in-progress, resolved, closed)
    - assigned_to: Email/ID of assigned support team member
    - response_sent: Whether response has been sent to submitter
    """
    try:
        contact_service = ContactService(session)
        updated_submission = contact_service.update_submission(
            submission_id=submission_id,
            update_data=update_data
        )

        if not updated_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission {submission_id} not found"
            )

        return ContactSubmissionPublic.model_validate(updated_submission)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update submission: {str(e)}"
        )


@router.get(
    "/stats",
    summary="Get submission statistics (Admin only)",
    description="Get count of submissions by status"
)
async def get_submission_stats(
    session: Session = Depends(get_session)
    # TODO: Add admin authentication dependency
    # current_user: User = Depends(get_current_admin_user)
) -> dict:
    """
    Get submission statistics (admin only)

    Returns count of submissions by status
    """
    try:
        contact_service = ContactService(session)
        stats = contact_service.count_submissions_by_status()
        return {
            "total": sum(stats.values()),
            "by_status": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
