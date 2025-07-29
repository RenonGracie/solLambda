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
        # Column exists, just ensure all NULL values are set to default
        op.execute(
            text("UPDATE signup SET payment_type = 'out_of_pocket' WHERE payment_type IS NULL")
        )
    else:
        # Column doesn't exist, add it
        op.add_column(
            'signup', 
            sa.Column('payment_type', sa.String(50), nullable=True, server_default='out_of_pocket')
        )
        
        # Update any NULL values to 'out_of_pocket'
        op.execute(
            text("UPDATE signup SET payment_type = 'out_of_pocket' WHERE payment_type IS NULL")
        )


def downgrade() -> None:
    # Don't drop the column on downgrade since 1.0.1 already handles the column
    # Just revert any data changes if needed
    pass
