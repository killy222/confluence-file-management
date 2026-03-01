"""Initial schema: runs and exported_files.

Revision ID: 20260224_1500
Revises:
Create Date: 2026-02-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260224_1500"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("script", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("log_output", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("parent_run_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_runs_script", "runs", ["script"], unique=False)
    op.create_index("ix_runs_status", "runs", ["status"], unique=False)
    op.create_index("ix_runs_parent_run_id", "runs", ["parent_run_id"], unique=False)
    op.create_foreign_key(
        "fk_runs_parent_run_id",
        "runs",
        "runs",
        ["parent_run_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "exported_files",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("page_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_exported_files_run_id", "exported_files", ["run_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_exported_files_run_id", table_name="exported_files")
    op.drop_table("exported_files")
    op.drop_constraint("fk_runs_parent_run_id", "runs", type_="foreignkey")
    op.drop_index("ix_runs_parent_run_id", table_name="runs")
    op.drop_index("ix_runs_status", table_name="runs")
    op.drop_index("ix_runs_script", table_name="runs")
    op.drop_table("runs")
