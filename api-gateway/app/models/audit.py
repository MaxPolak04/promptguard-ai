import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditAction(str, enum.Enum):
    """Outcome of a proxied chat request."""

    allowed = "allowed"
    blocked_prompt = "blocked_prompt"
    blocked_response = "blocked_response"


class AuditEvent(Base):
    """One inspection record per proxied chat request."""

    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    rule = Column(String(64), nullable=True)
    prompt: Mapped[str] = mapped_column(Text)
    response = Column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
