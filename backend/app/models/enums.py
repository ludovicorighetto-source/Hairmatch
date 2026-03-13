import enum

from sqlalchemy import Enum as SAEnum


class UserRole(str, enum.Enum):
    salon = "salon"
    professional = "professional"


class SubscriptionPlan(str, enum.Enum):
    free = "free"
    basic = "basic"
    premium = "premium"
    enterprise = "enterprise"


class AvailabilityStatus(str, enum.Enum):
    available = "available"
    partially_available = "partially_available"
    not_available = "not_available"
    on_leave = "on_leave"


# SQLAlchemy enum types (native PostgreSQL enums)
user_role_enum = SAEnum(
    UserRole,
    name="user_role",
    create_type=False,  # managed by Alembic migration
)

subscription_plan_enum = SAEnum(
    SubscriptionPlan,
    name="subscription_plan",
    create_type=False,
)

availability_status_enum = SAEnum(
    AvailabilityStatus,
    name="availability_status",
    create_type=False,
)


class JobStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    closed = "closed"


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"


job_status_enum = SAEnum(
    JobStatus,
    name="job_status",
    create_type=False,
)

application_status_enum = SAEnum(
    ApplicationStatus,
    name="application_status",
    create_type=False,
)
