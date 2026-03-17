"""Add notebook_targets table and notebook_name on runs.

Revision ID: 20260317_1300
Revises: 20260317_1200
Create Date: 2026-03-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260317_1300"
down_revision: Union[str, None] = "20260317_1200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_table(
      "notebook_targets",
      sa.Column("id", sa.UUID(), nullable=False),
      sa.Column("name", sa.String(length=255), nullable=False),
      sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
      sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
      sa.PrimaryKeyConstraint("id"),
  )
  op.create_index("ix_notebook_targets_name", "notebook_targets", ["name"], unique=True)

  op.add_column(
      "runs",
      sa.Column("notebook_name", sa.String(length=255), nullable=True),
  )


def downgrade() -> None:
  op.drop_column("runs", "notebook_name")
  op.drop_index("ix_notebook_targets_name", table_name="notebook_targets")
  op.drop_table("notebook_targets")

