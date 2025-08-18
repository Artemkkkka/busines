from typing import Optional
from pydantic import BaseModel, Field

from app.models.team import TeamRole

class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=3, max_length=64)

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    code: Optional[str] = Field(default=None, min_length=3, max_length=64)

class TeamRead(BaseModel):
    id: int
    name: str
    code: str
    owner_id: Optional[int]

    class Config:
        from_attributes = True

class MemberIn(BaseModel):
    user_id: int
    role: TeamRole = TeamRole.employee

class MemberUpdate(BaseModel):
    role: TeamRole

class MemberRead(BaseModel):
    user_id: int
    team_id: Optional[int]
    role_in_team: TeamRole

    class Config:
        from_attributes = True