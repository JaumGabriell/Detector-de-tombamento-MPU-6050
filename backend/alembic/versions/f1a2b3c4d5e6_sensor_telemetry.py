"""Store the latest telemetry per sensor.

Revision ID: f1a2b3c4d5e6
Revises: 1491ab40c158
"""

from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "1491ab40c158"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sensor_telemetry",
        sa.Column("sensor_id", sa.Integer(), sa.ForeignKey("sensors.id"), primary_key=True),
        sa.Column("data", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("sensor_telemetry")
