"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-11
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ Настоящие DDL-операции через alembic op
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("superadmin","moderator","seller","buyer",
                                   name="roleenum"), nullable=False, default="buyer"),
        sa.Column("referral_code", sa.String(20), nullable=False, unique=True),
        sa.Column("balance", sa.Numeric(12, 2), nullable=False, default=0),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_staff", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_user_email", "user", ["email"])
    op.create_index("ix_user_referral_code", "user", ["referral_code"])
    # ... остальные таблицы через op.create_table() ...


def downgrade() -> None:
    op.drop_table("user")
    # ... остальные drop в обратном порядке ...