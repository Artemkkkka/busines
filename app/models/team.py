import enum

from sqlalchemy import Enum, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Team(Base):
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)

    members: Mapped[list["UserTeam"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="team")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="team")


class TeamRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"


class UserTeam(Base):
    __tablename__ = "user_teams"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), primary_key=True)
    role_in_team: Mapped[TeamRole] = mapped_column(Enum(TeamRole, name="team_role"), nullable=False, default=TeamRole.employee)
    user: Mapped["User"] = relationship(back_populates="teams")
    team: Mapped["Team"] = relationship(back_populates="members")
