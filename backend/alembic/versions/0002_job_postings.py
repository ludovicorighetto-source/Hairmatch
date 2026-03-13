"""job_postings

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-01 00:00:00.000000

Creates:
  - Enum types: job_status, application_status
  - Tables: job_postings, job_applications
  - Indexes on FK and status columns
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enum types ─────────────────────────────────────────────────────────────
    job_status = postgresql.ENUM(
        "draft", "open", "closed", name="job_status", create_type=False
    )
    job_status.create(op.get_bind(), checkfirst=True)

    application_status = postgresql.ENUM(
        "pending", "accepted", "rejected", "withdrawn",
        name="application_status", create_type=False
    )
    application_status.create(op.get_bind(), checkfirst=True)

    # ── job_postings table ─────────────────────────────────────────────────────
    op.create_table(
        "job_postings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("salon_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "specializations",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "contract_types",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("province", sa.String(5), nullable=True),
        sa.Column("salary_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "open", "closed", name="job_status"),
            nullable=False,
            server_default="open",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["salon_id"], ["salon_profiles.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_postings_salon_id", "job_postings", ["salon_id"])
    op.create_index("ix_job_postings_status", "job_postings", ["status"])
    op.create_index("ix_job_postings_province", "job_postings", ["province"])

    # ── job_applications table ─────────────────────────────────────────────────
    op.create_table(
        "job_applications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("professional_id", sa.UUID(), nullable=False),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "rejected", "withdrawn", name="application_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["professional_id"], ["professional_profiles.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", "professional_id", name="uq_application_job_professional"),
    )
    op.create_index("ix_job_applications_job_id", "job_applications", ["job_id"])
    op.create_index(
        "ix_job_applications_professional_id", "job_applications", ["professional_id"]
    )
    op.create_index("ix_job_applications_status", "job_applications", ["status"])


def downgrade() -> None:
    op.drop_table("job_applications")
    op.drop_table("job_postings")
    op.execute("DROP TYPE IF EXISTS application_status")
    op.execute("DROP TYPE IF EXISTS job_status")
