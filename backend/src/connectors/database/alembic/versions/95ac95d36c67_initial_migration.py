"""Initial migration.

Revision ID: 95ac95d36c67
Revises:
Create Date: 2026-05-16 12:05:31.014341

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '95ac95d36c67'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    statustask = postgresql.ENUM(
        'backlog',
        'to_do',
        'in_progress',
        'on_review',
        'done',
        'cancelled',
        name='statustask',
        create_type=True,
    )
    statustask.create(bind, checkfirst=True)

    prioritytask = postgresql.ENUM(
        'low',
        'medium',
        'high',
        'critical',
        name='prioritytask',
        create_type=True,
    )
    prioritytask.create(bind, checkfirst=True)

    typetask = postgresql.ENUM(
        'feature',
        'bug',
        'documentation',
        'other',
        name='typetask',
        create_type=True,
    )
    typetask.create(bind, checkfirst=True)

    st_use = postgresql.ENUM(
        'backlog',
        'to_do',
        'in_progress',
        'on_review',
        'done',
        'cancelled',
        name='statustask',
        create_type=False,
    )
    pr_use = postgresql.ENUM(
        'low',
        'medium',
        'high',
        'critical',
        name='prioritytask',
        create_type=False,
    )
    ty_use = postgresql.ENUM(
        'feature',
        'bug',
        'documentation',
        'other',
        name='typetask',
        create_type=False,
    )

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', st_use, nullable=False),
        sa.Column('priority', pr_use, nullable=False),
        sa.Column('type', ty_use, nullable=False),
        sa.Column('pull_request_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tasks')
    op.drop_table('users')
    op.execute(sa.text('DROP TYPE IF EXISTS typetask'))
    op.execute(sa.text('DROP TYPE IF EXISTS prioritytask'))
    op.execute(sa.text('DROP TYPE IF EXISTS statustask'))
