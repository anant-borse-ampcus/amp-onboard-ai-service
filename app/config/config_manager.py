from functools import lru_cache

from app.config.settings import Settings, get_settings


class ConfigManager:
    """Centralized configuration manager for runtime access."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def app_name(self) -> str:
        return self._settings.app_name

    @property
    def app_version(self) -> str:
        return self._settings.app_version

    @property
    def app_env(self) -> str:
        return self._settings.app_env

    @property
    def debug(self) -> bool:
        return self._settings.debug

    @property
    def log_level(self) -> str:
        return self._settings.log_level

    @property
    def llm_provider(self) -> str:
        return self._settings.llm_provider

    def get_llm_config(self) -> dict[str, str]:
        """Return provider-specific LLM configuration."""
        if self._settings.llm_provider == "groq":
            return {
                "provider": "groq",
                "api_key": self._settings.groq_api_key,
                "model": self._settings.groq_model,
            }
        return {
            "provider": "openai",
            "api_key": self._settings.openai_api_key,
            "model": self._settings.openai_model,
        }


@lru_cache
def get_config_manager() -> ConfigManager:
    """Return cached configuration manager singleton."""
    return ConfigManager()
