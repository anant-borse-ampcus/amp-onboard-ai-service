"""Grounded FAQ engine with knowledge base retrieval."""

import json
from pathlib import Path

from app.llm.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.models.profile import EmployeeProfile
from app.schemas.llm_outputs import FAQAnswerOutput, FAQSourceOutput
from app.services.prompt import OutputParser, PromptBuilder

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "data" / "faq_knowledge.json"
CONFIDENCE_THRESHOLD = 0.5
FALLBACK_ANSWER = (
    "I don't have specific information about that. "
    "Please contact your onboarding buddy or HR for assistance."
)


class FAQEngine:
    """Provides grounded FAQ answers with hallucination prevention."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        output_parser: OutputParser,
        llm_provider: BaseLLMProvider,
        knowledge_path: Path | None = None,
        knowledge_repository=None,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._output_parser = output_parser
        self._llm_provider = llm_provider
        # When an admin-managed knowledge repository is provided, it is the source
        # of truth so KB edits are reflected in grounded answers immediately.
        self._knowledge_repository = knowledge_repository
        self._knowledge = self._load_knowledge(knowledge_path or KNOWLEDGE_PATH)

    def _load_knowledge(self, path: Path) -> list[dict]:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []

    def _knowledge_entries(self) -> list[dict]:
        if self._knowledge_repository is not None:
            return self._knowledge_repository.as_faq_dicts()
        return self._knowledge

    async def answer(
        self,
        question: str,
        profile: EmployeeProfile | None = None,
    ) -> FAQAnswerOutput:
        matches = self._retrieve(question)
        if matches:
            best = matches[0]
            confidence = min(0.95, 0.7 + 0.05 * len(matches))
            answer = best["answer"]
            if profile:
                answer = answer.replace("your manager", f"{profile.name}'s manager")
            return FAQAnswerOutput(
                question=question,
                answer=answer,
                sources=[
                    FAQSourceOutput(
                        title=best["title"],
                        url=best.get("url", ""),
                        excerpt=best.get("excerpt", ""),
                    )
                ],
                confidence=confidence,
                fallback=False,
            )

        grounded_context = self._build_knowledge_context()
        try:
            system_msg, user_msg = self._prompt_builder.build(
                "faq_answer",
                {
                    "name": profile.name if profile else "Employee",
                    "role": profile.role if profile else "Team Member",
                    "question": question,
                },
                extra_context=grounded_context,
            )
            response = await self._llm_provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=system_msg),
                        LLMMessage(role="user", content=user_msg),
                    ],
                    temperature=0.2,
                    metadata={"prompt_type": "faq_answer"},
                )
            )
            output = self._output_parser.parse_and_validate(
                response.content, FAQAnswerOutput
            )
            if output.confidence < CONFIDENCE_THRESHOLD or not output.answer.strip():
                return self._fallback(question)
            output.question = question
            if not self._is_grounded(output):
                return self._fallback(question)
            return output
        except Exception:
            return self._fallback(question)

    def _retrieve(self, question: str) -> list[dict]:
        """Retrieve knowledge base entries matching the question."""
        lower_q = question.lower()
        scored: list[tuple[int, dict]] = []

        for entry in self._knowledge_entries():
            score = 0
            for keyword in entry.get("keywords", []):
                if keyword.lower() in lower_q:
                    score += 2
            if entry.get("title", "").lower() in lower_q:
                score += 1
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored]

    def _build_knowledge_context(self) -> str:
        lines = ["Available knowledge base entries:"]
        for entry in self._knowledge_entries():
            lines.append(f"- {entry['title']}: {entry.get('excerpt', '')}")
        return "\n".join(lines)

    def _is_grounded(self, output: FAQAnswerOutput) -> bool:
        """Prevent hallucination by requiring sources for high-confidence answers."""
        if output.fallback:
            return True
        if output.confidence >= 0.8 and not output.sources:
            return False
        return True

    def _fallback(self, question: str) -> FAQAnswerOutput:
        return FAQAnswerOutput(
            question=question,
            answer=FALLBACK_ANSWER,
            sources=[],
            confidence=0.3,
            fallback=True,
        )
