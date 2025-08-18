"""normalize team_role and set default

Revision ID: 4ec1ab120ff1
Revises: c9a3b39ed7c9
Create Date: 2025-08-15 19:04:31.034040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ec1ab120ff1'
down_revision: Union[str, None] = 'c9a3b39ed7c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) admin -> manager (чтобы освободить имя 'admin')
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'admin'
        ) AND NOT EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'manager'
        ) THEN
            ALTER TYPE team_role RENAME VALUE 'admin' TO 'manager';
        END IF;
    END$$;
    """)

    # 2) owner -> admin
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'owner'
        ) AND NOT EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'admin'
        ) THEN
            ALTER TYPE team_role RENAME VALUE 'owner' TO 'admin';
        END IF;
    END$$;
    """)

    # 3) member -> employee
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'member'
        ) AND NOT EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'team_role' AND e.enumlabel = 'employee'
        ) THEN
            ALTER TYPE team_role RENAME VALUE 'member' TO 'employee';
        END IF;
    END$$;
    """)

    # 4) дефолт на колонку
    op.execute("ALTER TABLE workers ALTER COLUMN role_in_team SET DEFAULT 'employee'::team_role")


def downgrade() -> None:
    # снимаем дефолт
    op.execute("ALTER TABLE workers ALTER COLUMN role_in_team DROP DEFAULT")
