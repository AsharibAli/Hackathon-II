"""
Password reset service layer.
Handles password reset request, verification, and password update using 6-digit codes.
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone

from models.user import User
from models.password_reset import PasswordResetToken
from core.security import hash_password
from services.email import email_service


class PasswordResetService:
    """Service class for password reset operations."""

    @staticmethod
    def request_password_reset(session: Session, email: str) -> dict:
        """
        Request a password reset for the given email.
        Sends a 6-digit verification code if the user exists.

        Args:
            session: Database session
            email: User's email address

        Returns:
            Success message (same message regardless of whether user exists for security)
        """
        # Find user by email
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        # Always return success message to prevent email enumeration
        success_message = {
            "message": "If an account with that email exists, we've sent a verification code."
        }

        if not user:
            return success_message

        # Check if email service is configured
        if not email_service.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email service is not configured. Please contact support."
            )

        # Invalidate any existing codes for this user
        existing_tokens = session.exec(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used == False
            )
        ).all()
        
        for token in existing_tokens:
            token.used = True
            session.add(token)

        # Create new reset code
        reset_token = PasswordResetToken.create_code(user_id=user.id, email=user.email)
        session.add(reset_token)
        session.commit()

        # Send reset email with code
        try:
            email_service.send_password_reset_code(
                to_email=user.email,
                code=reset_token.token
            )
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Failed to send password reset email: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to send verification code. Please try again later."
            )

        return success_message

    @staticmethod
    def verify_code(session: Session, email: str, code: str) -> dict:
        """
        Verify if a password reset code is valid for the given email.

        Args:
            session: Database session
            email: User's email address
            code: The 6-digit verification code

        Returns:
            Token validity status with reset token for password update
        """
        # Find the most recent valid code for this email
        statement = select(PasswordResetToken).where(
            PasswordResetToken.email == email,
            PasswordResetToken.token == code,
            PasswordResetToken.used == False
        )
        reset_token = session.exec(statement).first()

        if not reset_token:
            return {"valid": False, "message": "Invalid verification code"}

        if not reset_token.is_valid():
            return {"valid": False, "message": "Verification code has expired"}

        return {"valid": True, "message": "Code verified successfully"}

    @staticmethod
    def reset_password(session: Session, email: str, code: str, new_password: str) -> dict:
        """
        Reset the user's password using a valid verification code.

        Args:
            session: Database session
            email: User's email address
            code: The 6-digit verification code
            new_password: The new password

        Returns:
            Success message

        Raises:
            HTTPException: If code is invalid or expired
        """
        # Find the reset token
        statement = select(PasswordResetToken).where(
            PasswordResetToken.email == email,
            PasswordResetToken.token == code,
            PasswordResetToken.used == False
        )
        reset_token = session.exec(statement).first()

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        if not reset_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired"
            )

        # Find the user
        user = session.exec(select(User).where(User.id == reset_token.user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update the password
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        # Mark the token as used
        reset_token.used = True

        session.add(user)
        session.add(reset_token)
        session.commit()

        return {"message": "Password has been reset successfully"}

