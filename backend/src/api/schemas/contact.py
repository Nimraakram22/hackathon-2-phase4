"""
Contact API Schemas
Pydantic schemas for contact form API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SubmissionStatus(str, Enum):
    """Contact submission workflow status"""
    NEW = "new"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ContactSubmissionCreate(BaseModel):
    """Schema for creating new contact submissions"""
    name: str = Field(..., min_length=1, max_length=100, description="Submitter's name")
    email: EmailStr = Field(..., max_length=255, description="Submitter's email address")
    subject: str = Field(..., min_length=1, max_length=200, description="Submission subject")
    message: str = Field(..., min_length=10, max_length=5000, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Feature Request",
                "message": "I would like to request a new feature for task prioritization."
            }
        }


class ContactSubmissionPublic(BaseModel):
    """Schema for public API responses"""
    id: int
    name: str
    email: str
    subject: str
    message: str
    status: SubmissionStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ContactSubmissionUpdate(BaseModel):
    """Schema for updating existing submissions (admin only)"""
    status: Optional[SubmissionStatus] = None
    assigned_to: Optional[str] = None
    response_sent: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "in-progress",
                "assigned_to": "support@example.com",
                "response_sent": False
            }
        }


class ContactSubmissionResponse(BaseModel):
    """Response after successful submission"""
    id: int
    message: str = "Your message has been received. We'll get back to you soon."
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "message": "Your message has been received. We'll get back to you soon.",
                "created_at": "2026-02-01T12:00:00Z"
            }
        }
