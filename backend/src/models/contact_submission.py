"""
ContactSubmission SQLModel
Database model for contact form submissions
"""
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SubmissionStatus(str, Enum):
    """Contact submission workflow status"""
    NEW = "new"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ContactSubmissionBase(SQLModel):
    """Base model with shared fields for create/update operations"""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(
        max_length=255,
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=10, max_length=5000)


class ContactSubmission(ContactSubmissionBase, table=True):
    """Database table model for contact submissions"""
    __tablename__ = "contact_submissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: SubmissionStatus = Field(default=SubmissionStatus.NEW, index=True)
    assigned_to: Optional[str] = Field(default=None, max_length=255)
    response_sent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)


class ContactSubmissionCreate(ContactSubmissionBase):
    """Schema for creating new submissions (API request)"""
    pass


class ContactSubmissionPublic(ContactSubmissionBase):
    """Schema for public API responses"""
    id: int
    status: SubmissionStatus
    created_at: datetime


class ContactSubmissionUpdate(SQLModel):
    """Schema for updating existing submissions (admin only)"""
    status: Optional[SubmissionStatus] = None
    assigned_to: Optional[str] = None
    response_sent: Optional[bool] = None
