"""add utm_field to client

Revision ID: 1d22f0b133d6
Revises:
Create Date: 2025-02-26 15:15:49.424254

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "1d22f0b133d6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    inspector = inspect(op.get_bind())
    columns = inspector.get_columns('clients')
    column_names = [column['name'] for column in columns]

    if 'utm_params' not in column_names:
        op.add_column("clients", sa.Column("utm_params", sa.Text, nullable=True))


def downgrade():
    op.drop_column("clients", "utm_params")
