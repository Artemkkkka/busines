from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Evaluation(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False, index=True)
    evaluator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text(), nullable=True)
    period_start: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("task_id", "evaluator_id", name="uq_evaluation_task_evaluator"),)
