"""accounting settings table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-14

"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounting_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("api_key_encrypted", sa.String(length=500), nullable=True),
    )
    op.create_index(
        "ix_accounting_settings_provider", "accounting_settings", ["provider"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_accounting_settings_provider", table_name="accounting_settings")
    op.drop_table("accounting_settings")
