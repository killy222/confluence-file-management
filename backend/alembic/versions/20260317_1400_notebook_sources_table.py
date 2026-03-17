"""Add notebook_sources table for tracking NotebookLM SOURCE_IDs.

Revision ID: 20260317_1400
Revises: 20260317_1300
Create Date: 2026-03-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260317_1400"
down_revision: Union[str, None] = "20260317_1300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notebook_sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("notebook_target_id", sa.UUID(), nullable=False),
        sa.Column("page_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("notebook_source_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["notebook_target_id"],
            ["notebook_targets.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_notebook_sources_target_page_title",
        "notebook_sources",
        ["notebook_target_id", "page_id", "title"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notebook_sources_target_page_title", table_name="notebook_sources")
    op.drop_table("notebook_sources")

