import uuid

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.llm import LLMClient
from app.models import User
from app.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Resolve the authenticated, active user from the Bearer token."""
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise unauthorized from None

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise unauthorized
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise unauthorized from None

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user


def get_llm_client(request: Request) -> LLMClient:
    """Return the shared LLM client created in the lifespan."""
    return request.app.state.llm_client
