from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Meeting(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    starts_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)

    team: Mapped["Team"] = relationship(back_populates="meetings")


Index("ix_meeting_team_time", Meeting.team_id, Meeting.starts_at, Meeting.ends_at)
