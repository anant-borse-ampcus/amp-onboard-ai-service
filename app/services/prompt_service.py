"""Prompt template loading and rendering utilities."""

import re
from pathlib import Path

from app.core.exceptions import ValidationError

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?prior",
    r"system\s+prompt",
    r"<\s*/?\s*script",
    r"jailbreak",
]


class PromptService:
    """Service for loading, rendering, and validating prompt templates."""

    def __init__(self, prompts_dir: Path | None = None) -> None:
        self._prompts_dir = prompts_dir or PROMPTS_DIR

    def load_template(self, template_name: str) -> str:
        """Load a prompt template by name."""
        path = self._prompts_dir / f"{template_name}.txt"
        if not path.exists():
            raise ValidationError(
                message=f"Prompt template not found: {template_name}",
                details={"path": str(path)},
            )
        return path.read_text(encoding="utf-8")

    def render(self, template_name: str, variables: dict[str, str]) -> str:
        """Render a prompt template with variable substitution."""
        template = self.load_template(template_name)
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def validate_input(self, user_input: str) -> str:
        """Sanitize user input and detect prompt injection attempts."""
        sanitized = user_input.strip()
        if len(sanitized) > 2000:
            raise ValidationError(
                message="Input exceeds maximum allowed length",
                details={"max_length": 2000},
            )

        lower = sanitized.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, lower):
                raise ValidationError(
                    message="Input contains disallowed content",
                    details={"reason": "potential_prompt_injection"},
                )

        return sanitized

    def validate_json_output(self, output: dict, required_keys: list[str]) -> dict:
        """Validate that LLM output contains required keys."""
        missing = [key for key in required_keys if key not in output]
        if missing:
            raise ValidationError(
                message="LLM output missing required fields",
                details={"missing_keys": missing},
            )
        return output
