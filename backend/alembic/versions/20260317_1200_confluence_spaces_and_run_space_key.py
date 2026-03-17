"""Add confluence_spaces table and space_key on runs.

Revision ID: 20260317_1200
Revises: 20260224_1500
Create Date: 2026-03-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260317_1200"
down_revision: Union[str, None] = "20260224_1500"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "confluence_spaces",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_confluence_spaces_key", "confluence_spaces", ["key"], unique=True)

    op.add_column(
        "runs",
        sa.Column("space_key", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_runs_space_key", "runs", ["space_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_runs_space_key", table_name="runs")
    op.drop_column("runs", "space_key")

    op.drop_index("ix_confluence_spaces_key", table_name="confluence_spaces")
    op.drop_table("confluence_spaces")

