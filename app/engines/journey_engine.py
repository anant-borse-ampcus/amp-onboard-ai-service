"""Journey generation engine with profile-aware personalization."""

from app.llm.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.models.journey import ChecklistItem, JourneyDay, JourneyTask, TaskType
from app.models.profile import EmployeeProfile, ExperienceLevel, LearningStyle
from app.schemas.llm_outputs import JourneyGenerationOutput, LLMDayOutput, LLMTaskOutput
from app.services.prompt import OutputParser, PromptBuilder


DAY_THEMES = [
    ("Welcome & Orientation", "Get oriented with the team and company culture."),
    ("Tools & Environment", "Set up your development environment and tools."),
    ("Core Concepts", "Learn fundamental concepts for your role."),
    ("Team Integration", "Collaborate with your team on initial tasks."),
    ("Hands-on Practice", "Apply your knowledge through practical exercises."),
    ("Advanced Topics", "Dive deeper into role-specific topics."),
    ("Project Work", "Contribute to a real project or task."),
    ("Review & Reflection", "Reflect on progress and plan next steps."),
]

TASK_TEMPLATES: dict[str, list[tuple[str, str, TaskType, int]]] = {
    "welcome": [
        ("Team Introduction Meeting", "Meet your team and understand the org structure.", TaskType.MEETING, 90),
        ("Company Culture Overview", "Learn about company values and culture.", TaskType.LEARNING, 60),
    ],
    "setup": [
        ("Development Environment Setup", "Configure IDE, tools, and access credentials.", TaskType.SETUP, 120),
        ("Repository Access & Clone", "Get access to code repositories and clone projects.", TaskType.SETUP, 60),
    ],
    "learning": [
        ("Architecture Overview", "Study the system architecture and key services.", TaskType.LEARNING, 90),
        ("Domain Knowledge Session", "Learn domain-specific concepts for your role.", TaskType.LEARNING, 90),
    ],
    "project": [
        ("First Code Contribution", "Complete a starter task or good-first-issue.", TaskType.PROJECT, 180),
        ("Pair Programming Session", "Work with a team member on a small task.", TaskType.PROJECT, 120),
    ],
    "review": [
        ("Self-Assessment", "Complete your onboarding self-assessment.", TaskType.REVIEW, 60),
        ("1:1 with Manager", "Discuss progress and blockers with your manager.", TaskType.MEETING, 60),
    ],
}

LEARNING_STYLE_TASKS: dict[LearningStyle, str] = {
    LearningStyle.VISUAL: "Watch overview videos and review architecture diagrams",
    LearningStyle.HANDS_ON: "Complete hands-on exercises and sandbox tasks",
    LearningStyle.READING: "Read documentation and write summary notes",
    LearningStyle.COLLABORATIVE: "Join team sessions and pair programming",
}


class JourneyEngine:
    """Generates personalized onboarding journeys based on employee profiles."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        output_parser: OutputParser,
        llm_provider: BaseLLMProvider,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._output_parser = output_parser
        self._llm_provider = llm_provider

    async def generate(self, profile: EmployeeProfile, total_days: int) -> JourneyGenerationOutput:
        """Generate a personalized journey, using LLM with rule-based fallback."""
        try:
            system_msg, user_msg = self._prompt_builder.build(
                "journey_generation",
                self._profile_variables(profile, total_days),
            )
            response = await self._llm_provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=system_msg),
                        LLMMessage(role="user", content=user_msg),
                    ],
                    temperature=0.3,
                    metadata={"prompt_type": "journey_generation"},
                )
            )
            output = self._output_parser.parse_and_validate(
                response.content, JourneyGenerationOutput
            )
            if len(output.days) >= 1:
                return self._enrich_journey(output, profile, total_days)
        except Exception:
            pass

        return self._generate_rule_based(profile, total_days)

    def _generate_rule_based(
        self, profile: EmployeeProfile, total_days: int
    ) -> JourneyGenerationOutput:
        """Rule-based journey generation using profile attributes."""
        days: list[LLMDayOutput] = []
        theme_keys = ["welcome", "setup", "learning", "project", "learning", "project", "review", "review"]
        tasks_per_day = 2 if profile.experience_level != ExperienceLevel.SENIOR else 1

        for day_num in range(1, total_days + 1):
            theme_idx = min(day_num - 1, len(DAY_THEMES) - 1)
            day_title, day_desc = DAY_THEMES[theme_idx]
            theme_key = theme_keys[min(day_num - 1, len(theme_keys) - 1)]

            base_tasks = TASK_TEMPLATES.get(theme_key, TASK_TEMPLATES["learning"])
            selected = base_tasks[:tasks_per_day]

            tasks: list[LLMTaskOutput] = []
            for title, desc, task_type, duration in selected:
                personalized_title = self._personalize_task_title(title, profile)
                personalized_desc = self._personalize_task_desc(desc, profile)
                adjusted_duration = self._adjust_duration(duration, profile.experience_level)
                checklist = self._build_checklist(personalized_title, profile)

                tasks.append(
                    LLMTaskOutput(
                        title=personalized_title,
                        description=personalized_desc,
                        task_type=task_type.value,
                        estimated_duration_minutes=adjusted_duration,
                        checklist_items=checklist,
                    )
                )

            if day_num == 1:
                tasks.append(
                    LLMTaskOutput(
                        title=f"{profile.team} Team Overview",
                        description=f"Learn about the {profile.team} team structure and goals.",
                        task_type=TaskType.LEARNING.value,
                        estimated_duration_minutes=60,
                        checklist_items=[
                            {"title": f"Review {profile.team} team wiki"},
                            {"title": "Meet team members"},
                        ],
                    )
                )

            days.append(
                LLMDayOutput(
                    day_number=day_num,
                    title=f"Day {day_num}: {day_title}",
                    description=day_desc.format(role=profile.role, team=profile.team),
                    tasks=tasks,
                )
            )

        summary = (
            f"Personalized {total_days}-day onboarding for {profile.name} "
            f"as {profile.role} on {profile.team}. "
            f"Pace: {profile.experience_level.value}, style: {profile.learning_style.value}."
        )
        return JourneyGenerationOutput(summary=summary, days=days)

    def _enrich_journey(
        self,
        output: JourneyGenerationOutput,
        profile: EmployeeProfile,
        total_days: int,
    ) -> JourneyGenerationOutput:
        """Enrich LLM output with profile-specific adjustments."""
        days = output.days[:total_days]
        for day in days:
            for task in day.tasks:
                if profile.team.lower() not in task.title.lower() and day.day_number <= 2:
                    task.description += f" Focus on {profile.team} team context."
        return JourneyGenerationOutput(summary=output.summary or self._generate_rule_based(profile, total_days).summary, days=days)

    def _personalize_task_title(self, title: str, profile: EmployeeProfile) -> str:
        if "Architecture" in title:
            return f"{profile.team} Architecture Overview"
        if "Domain" in title:
            return f"{profile.role} Domain Knowledge"
        return title

    def _personalize_task_desc(self, desc: str, profile: EmployeeProfile) -> str:
        style_hint = LEARNING_STYLE_TASKS.get(profile.learning_style, "")
        skills_hint = f" Leverage skills: {', '.join(profile.skills)}." if profile.skills else ""
        return f"{desc} {style_hint}.{skills_hint}"

    def _adjust_duration(self, base: int, level: ExperienceLevel) -> int:
        multipliers = {ExperienceLevel.JUNIOR: 1.3, ExperienceLevel.MID: 1.0, ExperienceLevel.SENIOR: 0.8}
        return int(base * multipliers.get(level, 1.0))

    def _build_checklist(self, task_title: str, profile: EmployeeProfile) -> list[dict]:
        items = [
            {"title": f"Review materials for {task_title}"},
            {"title": f"Complete {task_title} deliverable"},
        ]
        if profile.learning_style == LearningStyle.COLLABORATIVE:
            items.append({"title": "Schedule a sync with your buddy"})
        return items

    def _profile_variables(self, profile: EmployeeProfile, total_days: int) -> dict[str, str]:
        return {
            "name": profile.name,
            "role": profile.role,
            "team": profile.team,
            "experience_level": profile.experience_level.value,
            "skills": ", ".join(profile.skills),
            "learning_style": profile.learning_style.value,
            "start_date": profile.start_date,
            "total_days": str(total_days),
        }
