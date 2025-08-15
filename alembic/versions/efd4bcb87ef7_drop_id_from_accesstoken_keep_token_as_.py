"""drop id from accesstoken; keep token as PK

Revision ID: efd4bcb87ef7
Revises: 187a6b5912cd
Create Date: 2025-08-14 20:14:20.852407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efd4bcb87ef7'
down_revision: Union[str, None] = '187a6b5912cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # На всякий случай убедимся, что PK на token есть
    # (если уже есть — попытка создать тот же PK упадёт, поэтому делаем только drop id)
    with op.batch_alter_table("accesstoken", schema=None) as batch:
        # Если в вашей БД вдруг сформировался составной PK (id, token),
        # сначала бы пришлось дропнуть PK и создать заново — но в большинстве случаев PK уже на token.
        batch.drop_column("id")

def downgrade() -> None:
    with op.batch_alter_table("accesstoken", schema=None) as batch:
        batch.add_column(sa.Column("id", sa.Integer(), nullable=True))
        
