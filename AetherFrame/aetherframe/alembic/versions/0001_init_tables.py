"""Initial tables for plugins and jobs."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plugins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target", sa.String(length=256), nullable=False),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed", name="jobstatus"), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("plugin_id", sa.Integer(), sa.ForeignKey("plugins.id"), nullable=True),
    )

    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_plugins_id", "plugins", ["id"])


def downgrade():
    op.drop_index("ix_jobs_id", table_name="jobs")
    op.drop_index("ix_plugins_id", table_name="plugins")
    op.drop_table("jobs")
    op.drop_table("plugins")
    op.execute("DROP TYPE IF EXISTS jobstatus")
