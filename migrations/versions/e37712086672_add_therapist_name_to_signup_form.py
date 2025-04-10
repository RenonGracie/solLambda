"""add therapist name to signup form

Revision ID: e37712086672
Revises:
Create Date: 2025-04-09 16:58:56.881311

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.models.db.signup_form import ClientSignup

# revision identifiers, used by Alembic.
revision: str = "e37712086672"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns(ClientSignup.__tablename__)]

    if "therapist_name" not in columns:
        op.add_column(
            ClientSignup.__tablename__,
            sa.Column("therapist_name", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column(ClientSignup.__tablename__, "therapist_name")
