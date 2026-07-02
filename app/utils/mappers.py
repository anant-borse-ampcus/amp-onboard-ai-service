"""Mappers between domain entities and response DTOs."""

from app.models.journey import ChecklistItem, Journey, JourneyDay, JourneyTask
from app.models.profile import EmployeeProfile
from app.schemas.journey import (
    ChecklistItemResponse,
    JourneyDayResponse,
    JourneyResponse,
    JourneyTaskResponse,
)
from app.schemas.profile import ProfileResponse


def profile_to_response(profile: EmployeeProfile) -> ProfileResponse:
    return ProfileResponse(
        id=str(profile.id),
        name=profile.name,
        email=profile.email,
        role=profile.role,
        team=profile.team,
        experience_level=profile.experience_level,
        skills=profile.skills,
        learning_style=profile.learning_style,
        start_date=profile.start_date,
        manager_notes=profile.manager_notes,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


def checklist_to_response(item: ChecklistItem) -> ChecklistItemResponse:
    return ChecklistItemResponse(
        id=str(item.id),
        title=item.title,
        completed=item.completed,
    )


def task_to_response(task: JourneyTask) -> JourneyTaskResponse:
    return JourneyTaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        estimated_duration_minutes=task.estimated_duration_minutes,
        status=task.status,
        checklist_items=[checklist_to_response(c) for c in task.checklist_items],
    )


def day_to_response(day: JourneyDay) -> JourneyDayResponse:
    return JourneyDayResponse(
        id=str(day.id),
        day_number=day.day_number,
        title=day.title,
        description=day.description,
        tasks=[task_to_response(t) for t in day.tasks],
    )


def journey_to_response(journey: Journey) -> JourneyResponse:
    return JourneyResponse(
        id=str(journey.id),
        profile_id=str(journey.profile_id),
        version=journey.version,
        status=journey.status,
        days=[day_to_response(d) for d in journey.days],
        total_days=journey.total_days,
        summary=journey.summary,
        created_at=journey.created_at.isoformat(),
        updated_at=journey.updated_at.isoformat(),
    )
