"""
Password Reset API endpoints.
Handles forgot password, code verification, and password reset with 6-digit codes.
"""
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

from core.database import get_session
from services.password_reset import PasswordResetService


router = APIRouter()


# Request/Response Models
class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password."""
    email: EmailStr = Field(..., description="User's email address")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com"
            }
        }
    }


class ForgotPasswordResponse(BaseModel):
    """Response model for forgot password request."""
    message: str = Field(..., description="Status message")


class VerifyCodeRequest(BaseModel):
    """Request model for code verification."""
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$", description="6-digit verification code")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "code": "123456"
            }
        }
    }


class VerifyCodeResponse(BaseModel):
    """Response model for code verification."""
    valid: bool = Field(..., description="Whether the code is valid")
    message: str = Field(..., description="Status message")


class ResetPasswordRequest(BaseModel):
    """Request model for password reset."""
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$", description="6-digit verification code")
    password: str = Field(..., min_length=8, max_length=100, description="New password (min 8 characters)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "code": "123456",
                "password": "newSecurePassword123"
            }
        }
    }


class ResetPasswordResponse(BaseModel):
    """Response model for password reset."""
    message: str = Field(..., description="Status message")


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send a 6-digit verification code to the user's registered email address."
)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Annotated[Session, Depends(get_session)]
) -> ForgotPasswordResponse:
    """
    Request a password reset.

    - **email**: Registered email address

    If the email exists, a 6-digit verification code will be sent.
    For security, the same response is returned regardless of whether the email exists.
    """
    result = PasswordResetService.request_password_reset(
        session=session,
        email=request.email
    )
    return ForgotPasswordResponse(**result)


@router.post(
    "/verify-reset-code",
    response_model=VerifyCodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify reset code",
    description="Check if a 6-digit verification code is valid for the given email."
)
async def verify_reset_code(
    request: VerifyCodeRequest,
    session: Annotated[Session, Depends(get_session)]
) -> VerifyCodeResponse:
    """
    Verify a password reset code.

    - **email**: User's email address
    - **code**: The 6-digit verification code from the email

    Returns whether the code is valid and can be used to reset the password.
    """
    result = PasswordResetService.verify_code(
        session=session,
        email=request.email,
        code=request.code
    )
    return VerifyCodeResponse(**result)


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset the user's password using a valid 6-digit verification code."
)
async def reset_password(
    request: ResetPasswordRequest,
    session: Annotated[Session, Depends(get_session)]
) -> ResetPasswordResponse:
    """
    Reset the password with a valid verification code.

    - **email**: User's email address
    - **code**: Valid 6-digit verification code
    - **password**: New password (minimum 8 characters)

    The code will be invalidated after successful password reset.
    """
    result = PasswordResetService.reset_password(
        session=session,
        email=request.email,
        code=request.code,
        new_password=request.password
    )
    return ResetPasswordResponse(**result)

