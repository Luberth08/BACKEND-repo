"""Add check constraint to vehiculo.anio

Revision ID: f735b08c45c0
Revises: 5389e0a50adf
Create Date: 2026-04-11 23:58:54.327787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f735b08c45c0'
down_revision: Union[str, Sequence[str], None] = '5389e0a50adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        'check_vehiculo_anio',
        'vehiculo',
        'anio >= 1900 AND anio <= 2100'
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('check_vehiculo_anio', 'vehiculo', type_='check')
    pass
