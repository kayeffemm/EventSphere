"""add is_admin to users

Revision ID: a7721ad1709e
Revises: 
Create Date: 2025-05-28 15:51:40.950770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7721ad1709e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # add the is_admin column, defaulting to false
    op.add_column(
        'users',
        sa.Column(
            'is_admin',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('FALSE')
        )
    )
    # (optional) remove the server_default so future inserts inherit the SQLAlchemy default
    op.alter_column(
        'users',
        'is_admin',
        server_default=None,
    )


def downgrade() -> None:
    # drop the column on downgrade
    op.drop_column('users', 'is_admin')