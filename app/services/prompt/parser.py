"""Structured JSON parsing from LLM responses."""

import json
import re

from pydantic import BaseModel, ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError


class OutputParser:
    """Parse and validate structured JSON from LLM output."""

    JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)

    def parse_json(self, content: str) -> dict:
        """Extract and parse JSON from raw LLM content."""
        text = content.strip()

        block_match = self.JSON_BLOCK_PATTERN.search(text)
        if block_match:
            text = block_match.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError as exc:
                    raise ValidationError(
                        message="Failed to parse LLM JSON output",
                        details={"reason": str(exc)},
                    ) from exc
            raise ValidationError(
                message="LLM response does not contain valid JSON",
                details={"content_preview": text[:200]},
            )

    def parse_and_validate(self, content: str, schema: type[BaseModel]) -> BaseModel:
        """Parse JSON and validate against a Pydantic schema."""
        data = self.parse_json(content)
        try:
            return schema.model_validate(data)
        except PydanticValidationError as exc:
            raise ValidationError(
                message="LLM output failed schema validation",
                details={"errors": exc.errors()},
            ) from exc
