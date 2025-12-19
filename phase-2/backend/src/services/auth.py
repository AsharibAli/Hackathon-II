"""
Authentication service layer.
Handles user registration, login, and logout operations.
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import Optional

from models.user import User
from core.security import hash_password, verify_password, create_access_token
from datetime import datetime, timezone


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def register_user(session: Session, email: str, password: str) -> tuple[User, str]:
        """
        Register a new user account.

        Args:
            session: Database session
            email: User's email address
            password: Plain text password

        Returns:
            Tuple of (User, access_token)

        Raises:
            HTTPException: 400 if email already exists
        """
        # Check if user already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        return user, access_token

    @staticmethod
    def login_user(session: Session, email: str, password: str) -> tuple[User, str]:
        """
        Authenticate user and generate access token.

        Args:
            session: Database session
            email: User's email address
            password: Plain text password

        Returns:
            Tuple of (User, access_token)

        Raises:
            HTTPException: 401 if credentials are invalid
        """
        # Find user by email
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        return user, access_token

    @staticmethod
    def logout_user() -> dict:
        """
        Logout user (client-side token invalidation).

        In a JWT-based system, logout is primarily client-side.
        The client should delete the stored token.

        Returns:
            Success message
        """
        return {"message": "Successfully logged out"}
