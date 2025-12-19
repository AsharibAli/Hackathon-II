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
