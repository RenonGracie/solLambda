"""add calendar_fetched to therapist

Revision ID: 7b35559a7414
Revises: 1d22f0b133d6
Create Date: 2025-03-11 11:58:36.882605

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "7b35559a7414"
down_revision: Union[str, None] = "1d22f0b133d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = inspector.get_columns("therapists")
    column_names = [column["name"] for column in columns]

    if "calendar_fetched" not in column_names:
        op.add_column(
            "therapists",
            sa.Column("calendar_fetched", sa.Boolean, nullable=True, default=False),
        )


def downgrade() -> None:
    op.drop_column("therapists", "calendar_fetched")
