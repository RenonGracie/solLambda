"""add therapist name to signup form

Revision ID: e37712086672
Revises:
Create Date: 2025-04-09 16:58:56.881311

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

from src.models.db.signup_form import ClientSignup

# revision identifiers, used by Alembic.
revision: str = "e37712086672"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        text(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{ClientSignup.__tablename__}' 
            AND column_name = 'therapist_name'
            """
        )
    ).fetchall()

    if not result:
        op.add_column(
            ClientSignup.__tablename__,
            sa.Column("therapist_name", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column(ClientSignup.__tablename__, "therapist_name")
