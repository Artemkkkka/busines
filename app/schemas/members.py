from pydantic import BaseModel, ConfigDict

from app.models.team import TeamRole


class MemberIn(BaseModel):
    user_id: int
    role: TeamRole = TeamRole.employee


class MemberUpdate(BaseModel):
    role: TeamRole


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    team_id: int
    role_in_team: TeamRole
