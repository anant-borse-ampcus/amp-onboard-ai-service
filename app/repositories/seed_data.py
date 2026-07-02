"""Seed data for Phase 1 mock demonstrations."""

from uuid import UUID

from app.models.journey import (
    ChecklistItem,
    Journey,
    JourneyDay,
    JourneyStatus,
    JourneyTask,
    TaskStatus,
    TaskType,
)
from app.models.profile import EmployeeProfile, ExperienceLevel, LearningStyle
from app.models.user import User, UserRole

DEMO_PROFILE_ID = UUID("11111111-1111-1111-1111-111111111111")
DEMO_JOURNEY_ID = UUID("22222222-2222-2222-2222-222222222222")
DEMO_MANAGER_ID = UUID("33333333-3333-3333-3333-333333333333")
DEMO_EMPLOYEE_ID = UUID("44444444-4444-4444-4444-444444444444")
DEMO_ADMIN_ID = UUID("55555555-5555-5555-5555-555555555555")

DEMO_PASSWORD = "password123"


def get_demo_users(hash_fn) -> list[User]:
    """Return pre-seeded demo users (system admin + manager + employee)."""
    return [
        User(
            id=DEMO_ADMIN_ID,
            email="admin@example.com",
            name="Sky Nakamura",
            role=UserRole.SYSTEM_ADMIN,
            hashed_password=hash_fn(DEMO_PASSWORD),
        ),
        User(
            id=DEMO_MANAGER_ID,
            email="manager@example.com",
            name="Morgan Lee",
            role=UserRole.MANAGER,
            hashed_password=hash_fn(DEMO_PASSWORD),
        ),
        User(
            id=DEMO_EMPLOYEE_ID,
            email="alex.rivera@example.com",
            name="Alex Rivera",
            role=UserRole.EMPLOYEE,
            hashed_password=hash_fn(DEMO_PASSWORD),
            profile_id=str(DEMO_PROFILE_ID),
        ),
    ]


def get_demo_profile() -> EmployeeProfile:
    """Return a pre-seeded demo employee profile."""
    return EmployeeProfile(
        id=DEMO_PROFILE_ID,
        name="Alex Rivera",
        email="alex.rivera@example.com",
        role="Software Engineer",
        team="Platform Engineering",
        experience_level=ExperienceLevel.MID,
        skills=["Python", "React", "Docker"],
        learning_style=LearningStyle.HANDS_ON,
        start_date="2026-07-07",
        manager_notes="Focus on platform tooling and CI/CD pipelines.",
    )


def get_demo_journey() -> Journey:
    """Return a pre-seeded demo onboarding journey."""
    day1_tasks = [
        JourneyTask(
            title="Welcome & Team Introduction",
            description="Meet your team and understand the org structure.",
            task_type=TaskType.MEETING,
            estimated_duration_minutes=90,
            checklist_items=[
                ChecklistItem(title="Attend team standup"),
                ChecklistItem(title="Schedule 1:1 with manager"),
                ChecklistItem(title="Review team wiki"),
            ],
        ),
        JourneyTask(
            title="Development Environment Setup",
            description="Set up local dev environment and access credentials.",
            task_type=TaskType.SETUP,
            estimated_duration_minutes=120,
            checklist_items=[
                ChecklistItem(title="Clone main repositories"),
                ChecklistItem(title="Configure IDE and linters"),
                ChecklistItem(title="Verify local build passes"),
            ],
        ),
    ]

    day2_tasks = [
        JourneyTask(
            title="Platform Architecture Overview",
            description="Learn the core platform architecture and services.",
            task_type=TaskType.LEARNING,
            estimated_duration_minutes=90,
            checklist_items=[
                ChecklistItem(title="Read architecture docs"),
                ChecklistItem(title="Watch platform overview video"),
            ],
        ),
        JourneyTask(
            title="First Code Contribution",
            description="Complete a small starter task in the codebase.",
            task_type=TaskType.PROJECT,
            estimated_duration_minutes=180,
            checklist_items=[
                ChecklistItem(title="Pick a good-first-issue"),
                ChecklistItem(title="Submit PR for review"),
            ],
        ),
    ]

    day3_tasks = [
        JourneyTask(
            title="CI/CD Pipeline Deep Dive",
            description="Understand deployment pipelines and release process.",
            task_type=TaskType.LEARNING,
            estimated_duration_minutes=120,
            checklist_items=[
                ChecklistItem(title="Review pipeline configs"),
                ChecklistItem(title="Trigger a test deployment"),
            ],
        ),
        JourneyTask(
            title="Week 1 Retrospective",
            description="Reflect on progress and plan next steps with mentor.",
            task_type=TaskType.REVIEW,
            estimated_duration_minutes=60,
            checklist_items=[
                ChecklistItem(title="Complete self-assessment"),
                ChecklistItem(title="Discuss blockers with mentor"),
            ],
        ),
    ]

    return Journey(
        id=DEMO_JOURNEY_ID,
        profile_id=DEMO_PROFILE_ID,
        version=1,
        status=JourneyStatus.ACTIVE,
        total_days=3,
        summary="A personalized 3-day onboarding journey for a mid-level platform engineer.",
        days=[
            JourneyDay(
                day_number=1,
                title="Day 1: Welcome & Setup",
                description="Get oriented with the team and development environment.",
                tasks=day1_tasks,
            ),
            JourneyDay(
                day_number=2,
                title="Day 2: Platform Foundations",
                description="Learn core platform concepts and make your first contribution.",
                tasks=day2_tasks,
            ),
            JourneyDay(
                day_number=3,
                title="Day 3: Delivery & Reflection",
                description="Understand deployment workflows and reflect on week one.",
                tasks=day3_tasks,
            ),
        ],
    )
