
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


# -------------------------
# USER MODEL
# -------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default="employee", nullable=False
    )

    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="user"
    )


# -------------------------
# EVENT MODEL
# -------------------------

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="event"
    )


# -------------------------
# REGISTRATION MODEL
# -------------------------

class Registration(Base):
    __tablename__ = "registrations"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_id",
            name="unique_user_event_registration"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="registrations")
    event: Mapped["Event"] = relationship(back_populates="registrations")
