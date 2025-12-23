"""Add email column to password reset tokens

Revision ID: e1e327b9eb1b
Revises: 4d140a8bbf65
Create Date: 2025-12-23 12:56:49.777903

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'e1e327b9eb1b'
down_revision = '4d140a8bbf65'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Delete all existing tokens since they're invalid with the old schema
    op.execute("DELETE FROM password_reset_tokens")
    
    # Add email column
    op.add_column('password_reset_tokens', sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False))
    
    # Modify token column to be max 6 characters (for 6-digit codes)
    op.alter_column('password_reset_tokens', 'token',
               existing_type=sa.VARCHAR(length=255),
               type_=sqlmodel.sql.sqltypes.AutoString(length=6),
               existing_nullable=False)
    
    # Update index to not be unique (same code can be generated for different users)
    op.drop_index(op.f('ix_password_reset_tokens_token'), table_name='password_reset_tokens')
    op.create_index(op.f('ix_password_reset_tokens_token'), 'password_reset_tokens', ['token'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_password_reset_tokens_token'), table_name='password_reset_tokens')
    op.create_index(op.f('ix_password_reset_tokens_token'), 'password_reset_tokens', ['token'], unique=True)
    op.alter_column('password_reset_tokens', 'token',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=6),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    op.drop_column('password_reset_tokens', 'email')
