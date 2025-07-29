"""add payment type to signup form

Revision ID: 1.0.1_add_payment_type
Revises: c9f2e31a1caf
Create Date: 2025-07-22 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "1.0.1_add_payment_type"
down_revision: Union[str, None] = "c9f2e31a1caf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

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
            sa.Column('payment_type', sa.String(50), nullable=True, server_default='out_of_pocket')
        )

def downgrade() -> None:
    op.drop_column('signup', 'payment_type')
