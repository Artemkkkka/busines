"""add default to role_in_team

Revision ID: c9a3b39ed7c9
Revises: 939539431ff0
Create Date: 2025-08-15 18:59:03.679828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9a3b39ed7c9'
down_revision: Union[str, None] = '939539431ff0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'employee'
        ) THEN
            ALTER TABLE workers ALTER COLUMN role_in_team SET DEFAULT 'employee'::team_role;
        ELSE
            ALTER TABLE workers ALTER COLUMN role_in_team SET DEFAULT 'member'::team_role;
        END IF;
    END$$;
    """)

def downgrade() -> None:
    op.execute("ALTER TABLE workers ALTER COLUMN role_in_team DROP DEFAULT")
