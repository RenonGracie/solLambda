"""add payment type to signup form

Revision ID: 89dd2d1e127a
Revises: 1.0.1_add_payment_type
Create Date: 2025-07-22 15:38:34.436029

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "1.0.1_add_payment_type"
down_revision: str | None = "c9f2e31a1caf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    conn = op.get_bind()
    
    result = conn.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'signup' 
            AND column_name = 'payment_type'
        """)
    ).fetchall()
    
    if not result:
        op.add_column(
            'signup',
            sa.Column('payment_type', sa.String(50), nullable=True, default='out_of_pocket')
        )

def downgrade() -> None:
    op.drop_column('signup', 'payment_type')