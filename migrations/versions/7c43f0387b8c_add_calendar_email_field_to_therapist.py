"""add calendar email field to therapist

Revision ID: 7c43f0387b8c
Revises: 7b35559a7414
Create Date: 2025-03-17 16:48:11.860541

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "7c43f0387b8c"
down_revision: Union[str, None] = "7b35559a7414"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = inspector.get_columns("therapists")
    column_names = [column["name"] for column in columns]

    if "calendar_email" not in column_names:
        op.add_column(
            "therapists",
            sa.Column("calendar_email", sa.Text, nullable=True),
        )


def downgrade() -> None:
    op.drop_column("therapists", "calendar_email")
