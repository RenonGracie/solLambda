"""add discount field to signup form

Revision ID: 8c222d8a6a10
Revises: e37712086672
Create Date: 2025-04-24 11:40:06.541658

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from src.models.db.signup_form import ClientSignup

# revision identifiers, used by Alembic.
revision: str = "8c222d8a6a10"
down_revision: Union[str, None] = "e37712086672"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        text(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{ClientSignup.__tablename__}' 
            AND column_name = 'discount'
            """
        )
    ).fetchall()

    if not result:
        op.add_column(
            ClientSignup.__tablename__,
            sa.Column("discount", sa.Integer(), nullable=True, default=0),
        )


def downgrade() -> None:
    op.drop_column(ClientSignup.__tablename__, "discount")
