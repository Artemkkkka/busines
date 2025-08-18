import enum

from sqlalchemy import Enum, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Team(Base):
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)

    members: Mapped[list["Worker"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="team")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="team")


class TeamRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"


class Worker(Base):
    __tablename__ = "workers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("team.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    role_in_team: Mapped[TeamRole] = mapped_column(Enum(TeamRole, name="team_role"), nullable=False, default=TeamRole.employee)
    user: Mapped["User"] = relationship(back_populates="worker")
    team: Mapped["Team"] = relationship(back_populates="members")
