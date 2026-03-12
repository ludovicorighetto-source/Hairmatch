"""auth_initial

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

Creates:
  - Enum types: user_role, subscription_plan, availability_status
  - Tables: user_profiles, salon_profiles, professional_profiles
  - Indexes on FK and frequently queried columns
  - updated_at trigger function + triggers on all three tables
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# ── Revision identifiers ───────────────────────────────────────────────────────

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


# ── Upgrade ────────────────────────────────────────────────────────────────────

def upgrade() -> None:
    # ── 1. Create enum types ───────────────────────────────────────────────────
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('salon', 'professional');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE subscription_plan AS ENUM ('free', 'basic', 'premium', 'enterprise');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE availability_status AS ENUM (
                'available',
                'partially_available',
                'not_available',
                'on_leave'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    # ── 2. Create updated_at trigger function ──────────────────────────────────
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # ── 3. user_profiles ──────────────────────────────────────────────────────
    op.create_table(
        "user_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Must match Supabase auth.users.id",
        ),
        sa.Column(
            "role",
            sa.Enum("salon", "professional", name="user_role", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.execute(
        """
        CREATE TRIGGER trg_user_profiles_updated_at
        BEFORE UPDATE ON user_profiles
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    op.create_index("ix_user_profiles_role", "user_profiles", ["role"])
    op.create_index("ix_user_profiles_is_active", "user_profiles", ["is_active"])

    # ── 4. salon_profiles ─────────────────────────────────────────────────────
    op.create_table(
        "salon_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_profiles.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Business info
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("vat_number", sa.String(20), nullable=True, unique=True),
        sa.Column("phone", sa.String(30), nullable=False),
        sa.Column("website_url", sa.String(500), nullable=True),
        # Address
        sa.Column("address_street", sa.String(255), nullable=False),
        sa.Column("address_city", sa.String(100), nullable=False),
        sa.Column("address_province", sa.String(5), nullable=False),
        sa.Column("address_postal_code", sa.String(10), nullable=False),
        sa.Column(
            "address_country",
            sa.String(2),
            nullable=False,
            server_default=sa.text("'IT'"),
        ),
        # Geolocation
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        # Salon details
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("seats_count", sa.SmallInteger(), nullable=True),
        sa.Column("opening_hours", postgresql.JSONB(), nullable=True),
        # Media
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("cover_image_url", sa.String(500), nullable=True),
        # Subscription
        sa.Column(
            "subscription_plan",
            sa.Enum(
                "free", "basic", "premium", "enterprise",
                name="subscription_plan",
                create_type=False,
            ),
            nullable=False,
            server_default=sa.text("'free'"),
        ),
        sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True),
        # Profile status
        sa.Column(
            "is_profile_complete",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_featured",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.execute(
        """
        CREATE TRIGGER trg_salon_profiles_updated_at
        BEFORE UPDATE ON salon_profiles
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    op.create_index("ix_salon_profiles_user_id", "salon_profiles", ["user_id"])
    op.create_index("ix_salon_profiles_address_city", "salon_profiles", ["address_city"])
    op.create_index("ix_salon_profiles_address_province", "salon_profiles", ["address_province"])
    op.create_index("ix_salon_profiles_subscription_plan", "salon_profiles", ["subscription_plan"])
    op.create_index("ix_salon_profiles_is_featured", "salon_profiles", ["is_featured"])

    # ── 5. professional_profiles ──────────────────────────────────────────────
    op.create_table(
        "professional_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_profiles.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        # Personal info
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(30), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        # Professional details
        sa.Column(
            "specializations",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("years_of_experience", sa.SmallInteger(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        # Work preferences
        sa.Column("preferred_city", sa.String(100), nullable=True),
        sa.Column("preferred_province", sa.String(5), nullable=True),
        sa.Column(
            "max_travel_km",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "is_available_remotely",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "preferred_contract_types",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        # Availability
        sa.Column(
            "availability_status",
            sa.Enum(
                "available",
                "partially_available",
                "not_available",
                "on_leave",
                name="availability_status",
                create_type=False,
            ),
            nullable=False,
            server_default=sa.text("'available'"),
        ),
        # Media
        sa.Column("profile_photo_url", sa.String(500), nullable=True),
        sa.Column(
            "portfolio_urls",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        # Subscription
        sa.Column(
            "subscription_plan",
            sa.Enum(
                "free", "basic", "premium", "enterprise",
                name="subscription_plan",
                create_type=False,
            ),
            nullable=False,
            server_default=sa.text("'free'"),
        ),
        sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True),
        # Profile status
        sa.Column(
            "is_profile_complete",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_featured",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.execute(
        """
        CREATE TRIGGER trg_professional_profiles_updated_at
        BEFORE UPDATE ON professional_profiles
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    op.create_index("ix_professional_profiles_user_id", "professional_profiles", ["user_id"])
    op.create_index("ix_professional_profiles_preferred_city", "professional_profiles", ["preferred_city"])
    op.create_index("ix_professional_profiles_preferred_province", "professional_profiles", ["preferred_province"])
    op.create_index("ix_professional_profiles_availability_status", "professional_profiles", ["availability_status"])
    op.create_index("ix_professional_profiles_subscription_plan", "professional_profiles", ["subscription_plan"])
    op.create_index("ix_professional_profiles_is_featured", "professional_profiles", ["is_featured"])


# ── Downgrade ──────────────────────────────────────────────────────────────────

def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_professional_profiles_updated_at ON professional_profiles;")
    op.execute("DROP TRIGGER IF EXISTS trg_salon_profiles_updated_at ON salon_profiles;")
    op.execute("DROP TRIGGER IF EXISTS trg_user_profiles_updated_at ON user_profiles;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")

    # Drop tables (CASCADE handles FKs)
    op.drop_table("professional_profiles")
    op.drop_table("salon_profiles")
    op.drop_table("user_profiles")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS availability_status;")
    op.execute("DROP TYPE IF EXISTS subscription_plan;")
    op.execute("DROP TYPE IF EXISTS user_role;")
