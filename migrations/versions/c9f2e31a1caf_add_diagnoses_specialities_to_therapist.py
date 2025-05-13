"""add diagnoses_specialities to therapist

Revision ID: c9f2e31a1caf
Revises: 8c222d8a6a10
Create Date: 2025-05-13 11:59:18.502908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from src.models.db.airtable import AirtableTherapist

# revision identifiers, used by Alembic.
revision: str = 'c9f2e31a1caf'
down_revision: Union[str, None] = '8c222d8a6a10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    result = conn.execute(
        text(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{AirtableTherapist.__tablename__}' 
            AND column_name = 'diagnoses_specialities'
            """
        )
    ).fetchall()

    if not result:
        op.add_column(
            AirtableTherapist.__tablename__,
            sa.Column("diagnoses_specialities", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column(AirtableTherapist.__tablename__, "diagnoses_specialities")
