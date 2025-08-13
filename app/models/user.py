from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    global_role: Mapped[str] = mapped_column(String(20), default="user")

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    teams: Mapped[list["UserTeam"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    authored_tasks: Mapped[list["Task"]] = relationship(back_populates="author", foreign_keys="Task.author_id")
    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assignee", foreign_keys="Task.assignee_id")
