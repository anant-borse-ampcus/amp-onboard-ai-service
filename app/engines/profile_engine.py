"""Profile analysis engine."""

from app.llm.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.models.profile import EmployeeProfile, ExperienceLevel, LearningStyle
from app.schemas.llm_outputs import ProfileAnalysisOutput
from app.services.prompt import OutputParser, PromptBuilder

FOCUS_BY_LEVEL: dict[ExperienceLevel, list[str]] = {
    ExperienceLevel.JUNIOR: ["Fundamentals", "Codebase navigation", "Team communication"],
    ExperienceLevel.MID: ["Team processes", "Architecture patterns", "Cross-team collaboration"],
    ExperienceLevel.SENIOR: ["Technical leadership", "System design", "Mentoring others"],
}

PACE_BY_LEVEL: dict[ExperienceLevel, str] = {
    ExperienceLevel.JUNIOR: "Extended 7-10 day onboarding with extra support",
    ExperienceLevel.MID: "Standard 5-day onboarding with balanced tasks",
    ExperienceLevel.SENIOR: "Accelerated 3-5 day onboarding focusing on context",
}


class ProfileAnalysisEngine:
    """Analyzes employee profiles to inform journey personalization."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        output_parser: OutputParser,
        llm_provider: BaseLLMProvider,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._output_parser = output_parser
        self._llm_provider = llm_provider

    async def analyze(self, profile: EmployeeProfile) -> ProfileAnalysisOutput:
        try:
            system_msg, user_msg = self._prompt_builder.build(
                "profile_analysis",
                {
                    "name": profile.name,
                    "role": profile.role,
                    "team": profile.team,
                    "experience_level": profile.experience_level.value,
                    "skills": ", ".join(profile.skills),
                    "learning_style": profile.learning_style.value,
                },
            )
            response = await self._llm_provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=system_msg),
                        LLMMessage(role="user", content=user_msg),
                    ],
                    temperature=0.3,
                    metadata={"prompt_type": "profile_analysis"},
                )
            )
            return self._output_parser.parse_and_validate(
                response.content, ProfileAnalysisOutput
            )
        except Exception:
            return self._analyze_rule_based(profile)

    def _analyze_rule_based(self, profile: EmployeeProfile) -> ProfileAnalysisOutput:
        strengths = list(profile.skills) if profile.skills else ["Eager to learn", "Adaptable"]
        focus_areas = list(FOCUS_BY_LEVEL.get(profile.experience_level, FOCUS_BY_LEVEL[ExperienceLevel.MID]))

        if profile.learning_style == LearningStyle.HANDS_ON:
            focus_areas.append("Practical exercises")
        elif profile.learning_style == LearningStyle.VISUAL:
            focus_areas.append("Visual learning materials")

        if profile.manager_notes:
            focus_areas.append("Manager-specified priorities")

        pace = PACE_BY_LEVEL.get(profile.experience_level, PACE_BY_LEVEL[ExperienceLevel.MID])
        summary = (
            f"{profile.name} joins as {profile.role} on {profile.team}. "
            f"With {profile.experience_level.value} experience and "
            f"{profile.learning_style.value.replace('_', ' ')} learning preference, "
            f"recommend {pace.lower()}."
        )

        return ProfileAnalysisOutput(
            strengths=strengths,
            focus_areas=focus_areas,
            recommended_pace=pace,
            summary=summary,
        )
