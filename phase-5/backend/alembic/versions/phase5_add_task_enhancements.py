# [Task]: T011
# [Spec]: F-001, F-002, F-003, F-006, F-007
# [Description]: Alembic migration for Phase 5 Task model columns
"""Phase 5: Add task enhancements - priority, tags, due dates, reminders, recurrence

Revision ID: phase5_enhancements
Revises: e1e327b9eb1b
Create Date: 2025-12-25

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'phase5_enhancements'
down_revision: Union[str, None] = 'e1e327b9eb1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 5 columns to tasks table and create tags tables."""

    # Add new columns to tasks table
    op.add_column('tasks', sa.Column(
        'priority',
        sa.String(10),
        nullable=False,
        server_default='medium'
    ))

    op.add_column('tasks', sa.Column(
        'due_date',
        sa.DateTime(timezone=True),
        nullable=True
    ))

    op.add_column('tasks', sa.Column(
        'remind_at',
        sa.DateTime(timezone=True),
        nullable=True
    ))

    op.add_column('tasks', sa.Column(
        'reminder_sent',
        sa.Boolean(),
        nullable=False,
        server_default='false'
    ))

    op.add_column('tasks', sa.Column(
        'recurrence',
        sa.String(10),
        nullable=False,
        server_default='none'
    ))

    op.add_column('tasks', sa.Column(
        'parent_task_id',
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey('tasks.id'),
        nullable=True
    ))

    # Create indexes for new columns
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_reminder', 'tasks', ['remind_at', 'reminder_sent'])
    op.create_index('idx_tasks_parent', 'tasks', ['parent_task_id'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )

    # Create unique index for tag name per user
    op.create_index('idx_tags_name_user', 'tags', ['name', 'user_id'], unique=True)

    # Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('tasks.id', ondelete='CASCADE'),
                  primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('tags.id', ondelete='CASCADE'),
                  primary_key=True),
    )


def downgrade() -> None:
    """Remove Phase 5 columns and tables."""

    # Drop junction table first
    op.drop_table('task_tags')

    # Drop tags table
    op.drop_index('idx_tags_name_user', table_name='tags')
    op.drop_table('tags')

    # Drop indexes from tasks
    op.drop_index('idx_tasks_parent', table_name='tasks')
    op.drop_index('idx_tasks_reminder', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')

    # Drop columns from tasks
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence')
    op.drop_column('tasks', 'reminder_sent')
    op.drop_column('tasks', 'remind_at')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority')
