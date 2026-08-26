import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import UserRole


def _lowercase_email(value: str) -> str:
    # email-validator only lowercases the domain part; without this, the
    # local part's casing would let one person hold several accounts that
    # the audit log and duplicate-email check both treat as distinct.
    return value.lower()


class RegisterRequest(BaseModel):
    """Payload for creating a new account."""

    email: EmailStr
    password: str = Field(min_length=8)

    _normalize_email = field_validator("email")(_lowercase_email)


class LoginRequest(BaseModel):
    """Payload for obtaining an access token."""

    email: EmailStr
    password: str

    _normalize_email = field_validator("email")(_lowercase_email)


class TokenResponse(BaseModel):
    """A bearer access token."""

    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    """Public representation of a user account."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool


class ChatRequest(BaseModel):
    """A user prompt to proxy to the LLM provider."""

    prompt: str = Field(min_length=1, max_length=32000)


class ChatResponse(BaseModel):
    """The (possibly blocked) reply returned to the user."""

    response: str
    blocked: bool = False
