"""ajustes

Revision ID: e6e5f6fba857
Revises: 7075d949c2ab
Create Date: 2026-09-16 18:13:43.164347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision: str = "e6e5f6fba857"
down_revision: Union[str, Sequence[str], None] = "7075d949c2ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    with op.batch_alter_table("telegram_accounts") as batch_op:
        batch_op.alter_column(
            "chat_id",
            existing_type=sa.VARCHAR(),
            type_=sa.Integer(),
            nullable=True,
        )

def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("telegram_accounts") as batch_op:

        batch_op.alter_column(
            "chat_id",
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(),
            nullable=False,
        )

