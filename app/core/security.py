"""Password hashing and JWT token utilities."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.config.settings import Settings, get_settings
from app.core.exceptions import AppException

_PBKDF2_ROUNDS = 200_000
_PBKDF2_ALGO = "sha256"


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(
        self, message: str = "Authentication failed", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(AppException):
    """Raised when the user lacks permission for an action."""

    def __init__(
        self, message: str = "Not authorized", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO, password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ROUNDS
    )
    return f"pbkdf2${_PBKDF2_ROUNDS}${salt}${derived.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        scheme, rounds_str, salt, expected_hex = hashed.split("$")
    except ValueError:
        return False
    if scheme != "pbkdf2":
        return False
    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO, password.encode("utf-8"), salt.encode("utf-8"), int(rounds_str)
    )
    return hmac.compare_digest(derived.hex(), expected_hex)


def create_access_token(
    subject: str,
    role: str,
    extra: dict[str, Any] | None = None,
    settings: Settings | None = None,
) -> str:
    """Create a signed JWT access token."""
    settings = settings or get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    settings = settings or get_settings()
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError(message="Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError(message="Invalid authentication token") from exc
