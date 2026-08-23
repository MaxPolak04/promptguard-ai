from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, get_llm_client
from app.llm import LLMClient, LLMError
from app.models import AuditAction, AuditEvent, User
from app.rules import scan_text
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


async def _audit(
    session: AsyncSession,
    user: User,
    action: AuditAction,
    prompt: str,
    response: str | None = None,
    rule: str | None = None,
) -> None:
    """Persist one audit event for the request's outcome."""
    session.add(
        AuditEvent(
            user_id=user.id,
            action=action,
            prompt=prompt,
            response=response,
            rule=rule,
        )
    )
    await session.commit()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client),
) -> ChatResponse:
    """Proxy a prompt to the LLM provider with inspection in both directions."""
    prompt_match = scan_text(body.prompt)
    if prompt_match is not None:
        await _audit(
            session, user, AuditAction.blocked_prompt, body.prompt,
            rule=prompt_match.rule,
        )
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f"prompt blocked by rule: {prompt_match.rule}",
        )

    try:
        reply = await llm.complete(body.prompt)
    except LLMError as exc:
        # The prompt may already have reached the provider (e.g. a malformed
        # reply, as opposed to a connect/DNS failure), so it still gets an
        # audit row even though no usable response came back.
        await _audit(session, user, AuditAction.allowed, body.prompt)
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, detail="LLM provider unavailable"
        ) from exc

    response_match = scan_text(reply)
    if response_match is not None:
        await _audit(
            session, user, AuditAction.blocked_response, body.prompt,
            response=reply, rule=response_match.rule,
        )
        return ChatResponse(
            response=f"[response blocked by PromptGuard: {response_match.rule}]",
            blocked=True,
        )

    await _audit(session, user, AuditAction.allowed, body.prompt, response=reply)
    return ChatResponse(response=reply)
