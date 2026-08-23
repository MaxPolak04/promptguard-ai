import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole


class RegisterRequest(BaseModel):
    """Payload for creating a new account."""

    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """Payload for obtaining an access token."""

    email: EmailStr
    password: str


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

    prompt: str = Field(min_length=1)


class ChatResponse(BaseModel):
    """The (possibly blocked) reply returned to the user."""

    response: str
    blocked: bool = False
