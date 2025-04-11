"""cart item fix

Revision ID: cc0e02fe1d4f
Revises: 603d479378ec
Create Date: 2025-04-09 16:25:49.503723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc0e02fe1d4f'
down_revision: Union[str, None] = '603d479378ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('catalog', sa.Column('quantity', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('catalog', 'quantity')
    # ### end Alembic commands ###
