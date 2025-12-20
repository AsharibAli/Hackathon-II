"""
Authentication API endpoints.
Handles user registration, login, and logout.
"""
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

from core.database import get_session
from services.auth import AuthService
from api.dependencies import get_current_user
from models.user import User


router = APIRouter()


# Request/Response Models
class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password (min 8 characters)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "is_active": True
                }
            }
        }
    }


class LogoutResponse(BaseModel):
    """Response model for logout endpoint."""
    message: str = Field(..., description="Logout confirmation message")


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Returns user data and JWT token."
)
async def register(
    request: RegisterRequest,
    session: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters

    Returns JWT access token and user information.
    """
    user, access_token = AuthService.register_user(
        session=session,
        email=request.email,
        password=request.password
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active
        }
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password. Returns JWT token on success."
)
async def login(
    request: LoginRequest,
    session: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """
    Authenticate user and generate access token.

    - **email**: Registered email address
    - **password**: User's password

    Returns JWT access token and user information.
    """
    user, access_token = AuthService.login_user(
        session=session,
        email=request.email,
        password=request.password
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active
        }
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout the authenticated user. Client should delete the stored JWT token."
)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)]
) -> LogoutResponse:
    """
    Logout the authenticated user.

    Requires valid JWT token in Authorization header.
    Client should delete the stored token after receiving this response.
    """
    result = AuthService.logout_user()
    return LogoutResponse(**result)


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    id: str
    email: str
    full_name: str | None = None
    profile_picture: str | None = None
    is_active: bool


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""
    full_name: str | None = Field(None, max_length=100, description="User's full name")
    profile_picture: str | None = Field(None, max_length=500, description="URL to profile picture")


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user."
)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserProfileResponse:
    """Get the current user's profile."""
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        profile_picture=current_user.profile_picture,
        is_active=current_user.is_active
    )


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user."
)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> UserProfileResponse:
    """Update the current user's profile."""
    from datetime import datetime, timezone
    
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.profile_picture is not None:
        current_user.profile_picture = request.profile_picture
    
    current_user.updated_at = datetime.now(timezone.utc)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        profile_picture=current_user.profile_picture,
        is_active=current_user.is_active
    )
