"""ensure payment type has proper defaults and constraints

Revision ID: 1.0.2_add_payment_type_final
Revises: 1.0.1_add_payment_type
Create Date: 2025-07-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '1.0.2_add_payment_type_final'
down_revision: Union[str, None] = '1.0.1_add_payment_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Check if column already exists
    result = conn.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'signup' 
            AND column_name = 'payment_type'
        """)
    ).fetchall()
    
    if result:
        # Column exists, update any 'out_of_pocket' values to 'cash_pay'
        conn.execute(
            text("UPDATE signup SET payment_type = 'cash_pay' WHERE payment_type = 'out_of_pocket'")
        )
        
        # Update any NULL values to 'cash_pay'
        conn.execute(
            text("UPDATE signup SET payment_type = 'cash_pay' WHERE payment_type IS NULL")
        )
        
        # Update payment_type based on discount values
        conn.execute(
            text("""
                UPDATE signup 
                SET payment_type = CASE
                    WHEN discount = 100 THEN 'free'
                    WHEN discount = 50 THEN 'promo_code'
                    WHEN payment_type IN ('insurance', 'cash_pay', 'free', 'promo_code') THEN payment_type
                    ELSE 'cash_pay'
                END
            """)
        )
    else:
        # Column doesn't exist, add it with proper default
        op.add_column(
            'signup', 
            sa.Column('payment_type', sa.String(50), nullable=True, server_default='cash_pay')
        )
        
        # Set payment_type based on discount values for existing records
        conn.execute(
            text("""
                UPDATE signup 
                SET payment_type = CASE
                    WHEN discount = 100 THEN 'free'
                    WHEN discount = 50 THEN 'promo_code'
                    ELSE 'cash_pay'
                END
                WHERE payment_type IS NULL
            """)
        )


def downgrade() -> None:
    conn = op.get_bind()
    
    # Check if column exists
    result = conn.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'signup' 
            AND column_name = 'payment_type'
        """)
    ).fetchall()
    
    if result:
        # Revert 'cash_pay' back to 'out_of_pocket' for compatibility
        conn.execute(
            text("UPDATE signup SET payment_type = 'out_of_pocket' WHERE payment_type = 'cash_pay'")
        )