"""invoice type (gelir/gider)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-14

"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column("invoice_type", sa.String(length=10), nullable=False, server_default="gelir"),
    )


def downgrade() -> None:
    op.drop_column("invoices", "invoice_type")
