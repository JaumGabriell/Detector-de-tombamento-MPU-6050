"""allow multiple telegram accounts per user

Revision ID: d5e6f7a8b9c0
Revises: c4b8a1d2e3f4
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4b8a1d2e3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telegram_accounts_new",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("chat_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
    )
    op.execute(sa.text("""
        INSERT INTO telegram_accounts_new (id, user_id, username, chat_id)
        SELECT id, user_id, username, chat_id FROM telegram_accounts
    """))
    op.drop_table("telegram_accounts")
    op.rename_table("telegram_accounts_new", "telegram_accounts")


def downgrade() -> None:
    op.create_table(
        "telegram_accounts_old",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("chat_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
        sa.UniqueConstraint("user_id"),
    )
    op.execute(sa.text("""
        INSERT INTO telegram_accounts_old (id, user_id, username, chat_id)
        SELECT id, user_id, username, chat_id
        FROM telegram_accounts
        WHERE id IN (SELECT MIN(id) FROM telegram_accounts GROUP BY user_id)
    """))
    op.drop_table("telegram_accounts")
    op.rename_table("telegram_accounts_old", "telegram_accounts")
