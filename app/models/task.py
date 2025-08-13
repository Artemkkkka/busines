import enum

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TaskStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.open, index=True)
    deadline: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    team: Mapped["Team"] = relationship(back_populates="tasks")
    author: Mapped["User"] = relationship(back_populates="authored_tasks", foreign_keys=[author_id])
    assignee: Mapped["User | None"] = relationship(back_populates="assigned_tasks", foreign_keys=[assignee_id])
    comments: Mapped[list["TaskComment"]] = relationship(back_populates="task", cascade="all, delete-orphan")


Index("ix_task_team_status_deadline", Task.team_id, Task.status, Task.deadline)


class TaskComment(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped["Task"] = relationship(back_populates="comments")
