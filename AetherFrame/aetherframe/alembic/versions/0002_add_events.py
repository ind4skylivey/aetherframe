"""Add events table."""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_events"
down_revision = "0001_init_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=True),
    )
    op.create_index("ix_events_id", "events", ["id"])


def downgrade():
    op.drop_index("ix_events_id", table_name="events")
    op.drop_table("events")
