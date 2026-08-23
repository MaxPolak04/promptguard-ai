from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest, session: AsyncSession = Depends(get_session)
) -> User:
    """Create a new account with the default chat_user role."""
    result = await session.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="email already registered"
        )
    user = User(email=body.email, hashed_password=hash_password(body.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Verify credentials and issue a bearer token."""
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if (
        user is None
        or not verify_password(body.password, user.hashed_password)
        or not user.is_active
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    return TokenResponse(access_token=create_access_token(user.id, user.role.value))


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's own account."""
    return user
