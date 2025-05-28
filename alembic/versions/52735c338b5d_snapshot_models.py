"""snapshot models

Revision ID: 52735c338b5d
Revises: a7721ad1709e
Create Date: 2025-05-28 16:20:38.560723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '52735c338b5d'
down_revision: Union[str, None] = 'a7721ad1709e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # no-op snapshot, schema already matches models
    pass

def downgrade() -> None:
    # no-op
    pass
