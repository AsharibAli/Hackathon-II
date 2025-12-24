"""
Password reset token model for forgot password functionality.
Stores reset codes with expiration for secure password recovery.
"""
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from typing import Optional
import random


class PasswordResetToken(SQLModel, table=True):
    """
    Password reset token entity.
    Used for secure password reset flow via email verification with 6-digit code.
    """
    __tablename__ = "password_reset_tokens"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )

    # 6-digit verification code
    token: str = Field(
        index=True,
        max_length=6,
        nullable=False
    )

    # Store email for verification
    email: str = Field(
        max_length=255,
        nullable=False
    )

    expires_at: datetime = Field(
        nullable=False
    )

    used: bool = Field(
        default=False,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @classmethod
    def create_code(cls, user_id: UUID, email: str, expires_in_minutes: int = 15) -> "PasswordResetToken":
        """Create a new 6-digit password reset code."""
        # Generate random 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        return cls(
            user_id=user_id,
            token=code,
            email=email,
            expires_at=expires_at
        )

    def is_valid(self) -> bool:
        """Check if the code is valid (not expired and not used)."""
        # Use utcnow() for comparison to avoid timezone-aware vs naive issues
        # PostgreSQL stores timestamps without timezone info by default
        now = datetime.utcnow()
        expires = self.expires_at.replace(tzinfo=None) if self.expires_at.tzinfo else self.expires_at
        return not self.used and now < expires

