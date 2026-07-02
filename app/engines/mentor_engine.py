"""AI mentor engine for task-specific guidance."""

from app.llm.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.models.journey import Journey, JourneyTask, TaskStatus, TaskType
from app.models.profile import EmployeeProfile, LearningStyle
from app.schemas.llm_outputs import MentorGuidanceOutput
from app.services.prompt import OutputParser, PromptBuilder

TASK_TYPE_GUIDANCE: dict[TaskType, dict[str, str]] = {
    TaskType.LEARNING: {
        "purpose": "Build foundational knowledge for your role",
        "outcome": "You will understand key concepts and how they apply to your work",
        "duration": "1-2 hours",
    },
    TaskType.MEETING: {
        "purpose": "Build relationships and understand team dynamics",
        "outcome": "You will know your teammates and communication channels",
        "duration": "30-90 minutes",
    },
    TaskType.SETUP: {
        "purpose": "Prepare your development environment for productivity",
        "outcome": "You will have a fully configured workspace ready for coding",
        "duration": "1-3 hours",
    },
    TaskType.PROJECT: {
        "purpose": "Apply your knowledge through hands-on contribution",
        "outcome": "You will deliver a tangible contribution to the codebase",
        "duration": "2-4 hours",
    },
    TaskType.REVIEW: {
        "purpose": "Reflect on progress and identify areas for growth",
        "outcome": "You will have clear next steps and documented learnings",
        "duration": "30-60 minutes",
    },
}

STYLE_TIPS: dict[LearningStyle, list[str]] = {
    LearningStyle.VISUAL: ["Use diagrams and flowcharts", "Watch recorded walkthroughs"],
    LearningStyle.HANDS_ON: ["Try each step yourself before moving on", "Experiment in a sandbox"],
    LearningStyle.READING: ["Take notes as you read", "Summarize key points in your own words"],
    LearningStyle.COLLABORATIVE: ["Schedule pairing sessions", "Ask questions in team channels"],
}


class MentorEngine:
    """Generates personalized mentorship guidance for onboarding tasks."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        output_parser: OutputParser,
        llm_provider: BaseLLMProvider,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._output_parser = output_parser
        self._llm_provider = llm_provider

    async def get_guidance(
        self,
        profile: EmployeeProfile,
        journey: Journey,
        task: JourneyTask,
    ) -> MentorGuidanceOutput:
        progress_context = self._build_progress_context(journey)
        try:
            system_msg, user_msg = self._prompt_builder.build(
                "mentor_guidance",
                {
                    "name": profile.name,
                    "role": profile.role,
                    "team": profile.team,
                    "task_title": task.title,
                    "task_description": task.description,
                    "learning_style": profile.learning_style.value,
                },
                extra_context=progress_context,
            )
            response = await self._llm_provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=system_msg),
                        LLMMessage(role="user", content=user_msg),
                    ],
                    temperature=0.4,
                    metadata={"prompt_type": "mentor_guidance"},
                )
            )
            return self._output_parser.parse_and_validate(
                response.content, MentorGuidanceOutput
            )
        except Exception:
            return self._generate_rule_based(profile, task, journey)

    def _generate_rule_based(
        self,
        profile: EmployeeProfile,
        task: JourneyTask,
        journey: Journey,
    ) -> MentorGuidanceOutput:
        base = TASK_TYPE_GUIDANCE.get(task.task_type, TASK_TYPE_GUIDANCE[TaskType.LEARNING])
        style_tips = STYLE_TIPS.get(profile.learning_style, STYLE_TIPS[LearningStyle.HANDS_ON])

        completed = sum(
            1 for d in journey.days for t in d.tasks if t.status == TaskStatus.COMPLETED
        )
        total = sum(len(d.tasks) for d in journey.days)

        tips = [
            f"Break '{task.title}' into smaller steps",
            "Ask your onboarding buddy if you get stuck",
            *style_tips,
            "Document your learnings as you go",
        ]

        if completed > 0:
            tips.append(f"You've completed {completed}/{total} tasks — great progress!")

        prerequisites = ["Review team documentation"]
        if task.task_type in (TaskType.PROJECT, TaskType.SETUP):
            prerequisites.append("Ensure development environment is configured")

        return MentorGuidanceOutput(
            purpose=f"{base['purpose']}: {task.title}",
            learning_outcome=f"{base['outcome']} for {task.title}.",
            estimated_duration=base["duration"],
            prerequisites=prerequisites,
            tips=tips,
        )

    def _build_progress_context(self, journey: Journey) -> str:
        completed = sum(
            1 for d in journey.days for t in d.tasks if t.status == TaskStatus.COMPLETED
        )
        total = sum(len(d.tasks) for d in journey.days)
        return f"Progress: {completed}/{total} tasks completed. Journey version {journey.version}."
