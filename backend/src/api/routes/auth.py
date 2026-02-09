"""
Authentication routes.

This module provides endpoints for user registration, login, and profile retrieval.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.database.connection import get_session
from src.models.user import User
from src.api.auth_utils import hash_password, verify_password, create_access_token
from src.api.dependencies import get_current_user


router = APIRouter(prefix="/api/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password (min 8 characters)")


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Authentication response with user info and token."""

    user_id: UUID
    email: str
    access_token: str


class UserProfile(BaseModel):
    """User profile information."""

    user_id: UUID
    email: str
    created_at: str
    is_active: bool


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterRequest,
    session: Annotated[Session, Depends(get_session)],
) -> AuthResponse:
    """
    Register a new user account.

    Creates a new user with email and password authentication. Passwords are hashed
    using bcrypt before storage. Returns a JWT access token for immediate authentication.

    Args:
        request: Registration request with email and password
        session: Database session (injected)

    Returns:
        AuthResponse: User information and JWT access token

    Raises:
        HTTPException: 409 Conflict if email already registered
        HTTPException: 400 Bad Request if validation fails

    Example:
        ```bash
        curl -X POST http://localhost:8001/auth/register \\
          -H "Content-Type: application/json" \\
          -d '{"email": "user@example.com", "password": "securepass123"}'
        ```
    """
    # Check if email already exists
    existing_user = session.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = hash_password(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        access_token=access_token,
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    request: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
) -> AuthResponse:
    """
    Authenticate user with email and password.

    Validates user credentials and returns a JWT access token for authenticated requests.
    The token expires after 24 hours (configurable via JWT_EXPIRATION_MINUTES).

    Args:
        request: Login request with email and password
        session: Database session (injected)

    Returns:
        AuthResponse: User information and JWT access token

    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid or account is inactive

    Example:
        ```bash
        curl -X POST http://localhost:8001/auth/login \\
          -H "Content-Type: application/json" \\
          -d '{"email": "user@example.com", "password": "securepass123"}'
        ```
    """
    # Find user by email
    user = session.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        access_token=access_token,
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    """
    Get authenticated user's profile information.

    Returns the profile of the currently authenticated user based on the JWT token
    provided in the Authorization header.

    Args:
        current_user: Current authenticated user (injected from JWT token)

    Returns:
        UserProfile: User profile information including ID, email, creation date, and active status

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found

    Example:
        ```bash
        curl -X GET http://localhost:8001/auth/me \\
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
        ```
    """
    return UserProfile(
        user_id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
        is_active=current_user.is_active,
    )
