from fastapi_users_db_sqlalchemy  import SQLAlchemyBaseUserTable

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base, SQLAlchemyBaseUserTable[int]):
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    teams: Mapped[list["Worker"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    authored_tasks: Mapped[list["Task"]] = relationship(back_populates="author", foreign_keys="Task.author_id")
    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assignee", foreign_keys="Task.assignee_id")
