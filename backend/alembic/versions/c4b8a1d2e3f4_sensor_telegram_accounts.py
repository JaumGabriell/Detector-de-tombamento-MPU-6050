"""link sensors directly to telegram accounts

Revision ID: c4b8a1d2e3f4
Revises: e6e5f6fba857
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4b8a1d2e3f4"
down_revision: Union[str, Sequence[str], None] = "e6e5f6fba857"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sensor_telegram_accounts",
        sa.Column("sensor_id", sa.Integer(), nullable=False),
        sa.Column("telegram_account_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.id"]),
        sa.ForeignKeyConstraint(["telegram_account_id"], ["telegram_accounts.id"]),
        sa.PrimaryKeyConstraint("sensor_id", "telegram_account_id"),
    )
    op.execute(sa.text("""
        INSERT INTO sensor_telegram_accounts (sensor_id, telegram_account_id)
        SELECT sensor_users.sensor_id, telegram_accounts.id
        FROM sensor_users
        JOIN telegram_accounts ON telegram_accounts.user_id = sensor_users.user_id
    """))
    op.drop_table("sensor_users")


def downgrade() -> None:
    op.create_table(
        "sensor_users",
        sa.Column("sensor_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("sensor_id", "user_id"),
    )
    op.execute(sa.text("""
        INSERT INTO sensor_users (sensor_id, user_id)
        SELECT sensor_telegram_accounts.sensor_id, telegram_accounts.user_id
        FROM sensor_telegram_accounts
        JOIN telegram_accounts ON telegram_accounts.id = sensor_telegram_accounts.telegram_account_id
    """))
    op.drop_table("sensor_telegram_accounts")
