"""Journey regeneration engine with profile change detection."""

from app.llm.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.models.journey import Journey, JourneyTask, TaskType
from app.models.profile import EmployeeProfile
from app.models.profile_snapshot import ProfileDiff, ProfileSnapshot
from app.schemas.llm_outputs import JourneyRegenerationOutput, RegenerationTaskOutput
from app.services.prompt import OutputParser, PromptBuilder


class RegenerationEngine:
    """Detects profile changes and regenerates impacted journey tasks."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        output_parser: OutputParser,
        llm_provider: BaseLLMProvider,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._output_parser = output_parser
        self._llm_provider = llm_provider

    def detect_changes(
        self, previous: ProfileSnapshot, current: EmployeeProfile
    ) -> ProfileDiff:
        """Detect which profile fields changed."""
        diff = ProfileDiff(
            previous_role=previous.role,
            previous_team=previous.team,
            previous_experience=previous.experience_level.value,
            previous_skills=", ".join(previous.skills),
            current_role=current.role,
            current_team=current.team,
            current_experience=current.experience_level.value,
            current_skills=", ".join(current.skills),
        )

        if previous.role != current.role:
            diff.role_changed = True
            diff.changed_fields.append("role")
        if previous.team != current.team:
            diff.team_changed = True
            diff.changed_fields.append("team")
        if previous.experience_level != current.experience_level:
            diff.experience_changed = True
            diff.changed_fields.append("experience_level")
        if set(previous.skills) != set(current.skills):
            diff.skills_changed = True
            diff.changed_fields.append("skills")
        if previous.learning_style != current.learning_style:
            diff.learning_style_changed = True
            diff.changed_fields.append("learning_style")

        return diff

    async def regenerate(
        self,
        profile: EmployeeProfile,
        previous_journey: Journey,
        diff: ProfileDiff,
    ) -> JourneyRegenerationOutput:
        if not diff.has_changes:
            return JourneyRegenerationOutput(
                summary="No profile changes detected. Journey unchanged.",
            )

        try:
            system_msg, user_msg = self._prompt_builder.build(
                "journey_regeneration",
                {
                    "previous_role": diff.previous_role,
                    "previous_team": diff.previous_team,
                    "previous_experience": diff.previous_experience,
                    "previous_skills": diff.previous_skills,
                    "role": diff.current_role,
                    "team": diff.current_team,
                    "experience_level": diff.current_experience,
                    "skills": diff.current_skills,
                },
                extra_context=self._journey_summary(previous_journey),
            )
            response = await self._llm_provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=system_msg),
                        LLMMessage(role="user", content=user_msg),
                    ],
                    temperature=0.3,
                    metadata={"prompt_type": "journey_regeneration"},
                )
            )
            return self._output_parser.parse_and_validate(
                response.content, JourneyRegenerationOutput
            )
        except Exception:
            return self._regenerate_rule_based(profile, previous_journey, diff)

    def _regenerate_rule_based(
        self,
        profile: EmployeeProfile,
        previous_journey: Journey,
        diff: ProfileDiff,
    ) -> JourneyRegenerationOutput:
        added: list[RegenerationTaskOutput] = []
        modified: list[RegenerationTaskOutput] = []
        removed: list[RegenerationTaskOutput] = []

        if diff.team_changed:
            added.append(
                RegenerationTaskOutput(
                    title=f"{profile.team} Team-Specific Training",
                    description=f"New training module for the {profile.team} team.",
                    task_type=TaskType.LEARNING.value,
                    estimated_duration_minutes=90,
                    reason=f"Team changed from {diff.previous_team} to {diff.current_team}",
                )
            )
            for day in previous_journey.days:
                for task in day.tasks:
                    if diff.previous_team.lower() in task.title.lower():
                        modified.append(
                            RegenerationTaskOutput(
                                previous_title=task.title,
                                title=task.title.replace(diff.previous_team, profile.team),
                                description=f"Updated for {profile.team} team context.",
                                task_type=task.task_type.value,
                                reason="Team change requires updated content",
                            )
                        )

        if diff.role_changed:
            added.append(
                RegenerationTaskOutput(
                    title=f"{profile.role} Role Overview",
                    description=f"Learn responsibilities and expectations for {profile.role}.",
                    task_type=TaskType.LEARNING.value,
                    estimated_duration_minutes=60,
                    reason=f"Role changed from {diff.previous_role} to {diff.current_role}",
                )
            )

        if diff.experience_changed:
            modified.append(
                RegenerationTaskOutput(
                    previous_title="Self-Assessment",
                    title=f"Self-Assessment ({profile.experience_level.value} level)",
                    description="Adjusted assessment for new experience level.",
                    task_type=TaskType.REVIEW.value,
                    reason=f"Experience level changed to {diff.current_experience}",
                )
            )

        if diff.skills_changed:
            new_skills = set(profile.skills) - set(diff.previous_skills.split(", ") if diff.previous_skills else [])
            for skill in new_skills:
                if skill.strip():
                    added.append(
                        RegenerationTaskOutput(
                            title=f"Learn: {skill.strip()}",
                            description=f"Training module for new skill: {skill.strip()}.",
                            task_type=TaskType.LEARNING.value,
                            reason="New skill added to profile",
                        )
                    )

        if diff.learning_style_changed:
            modified.append(
                RegenerationTaskOutput(
                    previous_title="Architecture Overview",
                    title="Updated Learning Materials",
                    description=f"Materials adapted for {profile.learning_style.value} learning style.",
                    task_type=TaskType.LEARNING.value,
                    reason="Learning style preference changed",
                )
            )

        obsolete = []
        if diff.team_changed:
            obsolete = [
                t.title for d in previous_journey.days for t in d.tasks
                if diff.previous_team.lower() in t.title.lower() and diff.previous_team != profile.team
            ]
        for title in obsolete[:1]:
            removed.append(
                RegenerationTaskOutput(
                    previous_title=title,
                    reason=f"No longer relevant after team change to {profile.team}",
                )
            )

        summary = (
            f"Regenerated based on changes: {', '.join(diff.changed_fields)}. "
            f"{len(added)} added, {len(modified)} modified, {len(removed)} removed."
        )
        return JourneyRegenerationOutput(
            added=added, modified=modified, removed=removed, summary=summary
        )

    def apply_changes(
        self, previous_journey: Journey, changes: JourneyRegenerationOutput
    ) -> dict:
        """Apply regeneration changes to journey structure, only on impacted tasks."""
        days = []
        for day in previous_journey.days:
            tasks = list(day.tasks)

            for mod in changes.modified:
                for i, task in enumerate(tasks):
                    if task.title == mod.previous_title:
                        tasks[i] = JourneyTask(
                            title=mod.title or task.title,
                            description=mod.description or task.description,
                            task_type=TaskType(mod.task_type) if mod.task_type else task.task_type,
                            estimated_duration_minutes=mod.estimated_duration_minutes or task.estimated_duration_minutes,
                            status=task.status,
                            checklist_items=task.checklist_items,
                        )

            for rem in changes.removed:
                tasks = [t for t in tasks if t.title != rem.previous_title]

            if day.day_number == 1:
                for added in changes.added:
                    tasks.append(
                        JourneyTask(
                            title=added.title,
                            description=added.description,
                            task_type=TaskType(added.task_type) if added.task_type else TaskType.LEARNING,
                            estimated_duration_minutes=added.estimated_duration_minutes,
                        )
                    )

            days.append({
                "day_number": day.day_number,
                "title": day.title,
                "description": day.description,
                "tasks": [
                    {
                        "title": t.title,
                        "description": t.description,
                        "task_type": t.task_type.value,
                        "estimated_duration_minutes": t.estimated_duration_minutes,
                        "checklist_items": [{"title": c.title} for c in t.checklist_items],
                    }
                    for t in tasks
                ],
            })

        return {"summary": changes.summary, "days": days}

    def _journey_summary(self, journey: Journey) -> str:
        task_count = sum(len(d.tasks) for d in journey.days)
        return f"Previous journey v{journey.version}: {journey.total_days} days, {task_count} tasks."
