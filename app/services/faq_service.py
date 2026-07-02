from uuid import UUID

from app.engines.faq_engine import FAQEngine
from app.models.faq import FAQSource
from app.repositories.profile_repository import ProfileRepository
from app.schemas.faq import FAQRequest, FAQResponse
from app.services.prompt_service import PromptService


class FAQService:
    """Service for grounded FAQ responses."""

    def __init__(
        self,
        profile_repository: ProfileRepository,
        faq_engine: FAQEngine,
        prompt_service: PromptService,
    ) -> None:
        self._profile_repo = profile_repository
        self._faq_engine = faq_engine
        self._prompt_service = prompt_service

    async def ask(self, request: FAQRequest) -> FAQResponse:
        sanitized_question = self._prompt_service.validate_input(request.question)

        profile = None
        if request.profile_id:
            profile = await self._profile_repo.get_by_id(UUID(request.profile_id))

        output = await self._faq_engine.answer(sanitized_question, profile)

        return FAQResponse(
            question=sanitized_question,
            answer=output.answer,
            sources=[
                FAQSource(title=s.title, url=s.url, excerpt=s.excerpt)
                for s in output.sources
            ],
            confidence=output.confidence,
            fallback=output.fallback,
        )
