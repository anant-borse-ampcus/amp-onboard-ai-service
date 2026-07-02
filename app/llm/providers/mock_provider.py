"""Mock LLM provider for Phase 1 development without real API calls."""

import json
from typing import Any

from app.config.config_manager import ConfigManager
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider returning structured JSON responses."""

    def __init__(self, config_manager: ConfigManager | None = None) -> None:
        self._config_manager = config_manager

    @property
    def provider_name(self) -> str:
        return "mock"

    async def is_available(self) -> bool:
        return True

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a mock structured response based on prompt metadata."""
        prompt_type = request.metadata.get("prompt_type", "generic")
        variables = request.metadata.get("variables", {})

        content = self._generate_mock_response(prompt_type, variables)
        logger.info("Mock LLM generated response for prompt_type=%s", prompt_type)

        return LLMResponse(
            content=json.dumps(content),
            model="mock-gpt-4",
            provider=self.provider_name,
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            metadata={"prompt_type": prompt_type, "mock": True},
        )

    def _generate_mock_response(
        self, prompt_type: str, variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Return mock structured data for each prompt type."""
        generators = {
            "journey_generation": self._mock_journey,
            "mentor_guidance": self._mock_mentor,
            "faq_answer": self._mock_faq,
            "profile_analysis": self._mock_profile_analysis,
            "journey_regeneration": self._mock_regeneration,
        }
        generator = generators.get(prompt_type, self._mock_generic)
        return generator(variables)

    def _mock_journey(self, variables: dict[str, Any]) -> dict[str, Any]:
        total_days = int(variables.get("total_days", 5))
        role = variables.get("role", "Engineer")
        return {
            "summary": f"Personalized {total_days}-day onboarding journey for {role}.",
            "days": [
                {
                    "day_number": day,
                    "title": f"Day {day}: {'Welcome & Setup' if day == 1 else 'Core Skills' if day == 2 else 'Advanced Topics' if day < total_days else 'Review & Next Steps'}",
                    "description": f"Day {day} activities for {role}.",
                    "tasks": [
                        {
                            "title": f"Day {day} - Task 1",
                            "description": f"Primary learning activity for day {day}.",
                            "task_type": "learning" if day % 2 else "project",
                            "estimated_duration_minutes": 90,
                            "checklist_items": [
                                {"title": f"Complete day {day} reading"},
                                {"title": f"Practice day {day} exercise"},
                            ],
                        },
                        {
                            "title": f"Day {day} - Task 2",
                            "description": f"Hands-on activity for day {day}.",
                            "task_type": "project",
                            "estimated_duration_minutes": 120,
                            "checklist_items": [
                                {"title": f"Submit day {day} deliverable"},
                            ],
                        },
                    ],
                }
                for day in range(1, total_days + 1)
            ],
        }

    def _mock_mentor(self, variables: dict[str, Any]) -> dict[str, Any]:
        task_title = variables.get("task_title", "Task")
        return {
            "purpose": f"Help you successfully complete: {task_title}",
            "learning_outcome": f"You will understand the key concepts and deliverables for {task_title}.",
            "estimated_duration": "1-2 hours",
            "prerequisites": ["Review team documentation", "Set up development environment"],
            "tips": [
                "Break the task into smaller steps",
                "Ask your buddy if you get stuck",
                "Document your learnings as you go",
            ],
        }

    def _mock_faq(self, variables: dict[str, Any]) -> dict[str, Any]:
        question = variables.get("question", "")
        known_answers = {
            "vpn": {
                "answer": "Connect to the corporate VPN using the IT-provided client. Credentials are in your welcome email.",
                "sources": [{"title": "IT Setup Guide", "url": "/docs/it-setup", "excerpt": "VPN setup instructions"}],
                "confidence": 0.95,
                "fallback": False,
            },
            "benefits": {
                "answer": "Benefits enrollment opens on your first day. Visit the HR portal to select your plan.",
                "sources": [{"title": "HR Benefits Portal", "url": "/docs/benefits", "excerpt": "Benefits enrollment guide"}],
                "confidence": 0.92,
                "fallback": False,
            },
        }

        lower_q = question.lower()
        for keyword, response in known_answers.items():
            if keyword in lower_q:
                return {**response, "question": question}

        return {
            "question": question,
            "answer": "I don't have specific information about that. Please contact your onboarding buddy or HR for assistance.",
            "sources": [],
            "confidence": 0.3,
            "fallback": True,
        }

    def _mock_profile_analysis(self, variables: dict[str, Any]) -> dict[str, Any]:
        name = variables.get("name", "Employee")
        skills = variables.get("skills", "")
        return {
            "strengths": [s.strip() for s in skills.split(",") if s.strip()] or ["Eager to learn"],
            "focus_areas": ["Team processes", "Codebase familiarity", "Communication"],
            "recommended_pace": "Standard 5-day onboarding with hands-on tasks",
            "summary": f"{name} shows strong potential. Recommend a balanced mix of learning and practical tasks.",
        }

    def _mock_regeneration(self, variables: dict[str, Any]) -> dict[str, Any]:
        return {
            "added": [
                {
                    "title": "Advanced Team-Specific Training",
                    "description": "New training module for updated team assignment.",
                    "task_type": "learning",
                    "estimated_duration_minutes": 90,
                    "reason": "Team changed - new domain knowledge required",
                }
            ],
            "modified": [
                {
                    "previous_title": "Platform Architecture Overview",
                    "title": "Updated Architecture for New Team",
                    "description": "Revised architecture overview for the new team.",
                    "task_type": "learning",
                    "estimated_duration_minutes": 90,
                    "reason": "Team change requires different architecture focus",
                }
            ],
            "removed": [
                {
                    "previous_title": "Legacy System Introduction",
                    "reason": "No longer relevant for new team assignment",
                }
            ],
            "summary": "Journey updated based on profile changes. 1 task added, 1 modified, 1 removed.",
        }

    def _mock_generic(self, _variables: dict[str, Any]) -> dict[str, Any]:
        return {"message": "Mock response generated successfully."}
