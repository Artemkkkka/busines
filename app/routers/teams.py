from typing import List

from fastapi import APIRouter, status

from app.core.dependencies import SessionDep, CurrentUser
from app.schemas.teams import TeamCreate, TeamUpdate, TeamRead
from app.services import teams as svc_teams


teams_router = APIRouter(prefix="/teams", tags=["teams"])


@teams_router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(payload: TeamCreate, session: SessionDep, user: CurrentUser):
    team = await svc_teams.create_team(session, actor=user, name=payload.name, code=payload.code)
    return team


@teams_router.get("/", response_model=List[TeamRead])
async def list_teams(session: SessionDep, user: CurrentUser):
    return await svc_teams.list_teams_for_user(session, actor=user)


@teams_router.get("/{team_id}", response_model=TeamRead)
async def get_team(team_id: int, session: SessionDep, user: CurrentUser):
    return await svc_teams.get_team_for_user(session, actor=user, team_id=team_id)


@teams_router.patch("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, payload: TeamUpdate, session: SessionDep, user: CurrentUser):
    return await svc_teams.update_team(
        session, actor=user, team_id=team_id, name=payload.name, code=payload.code
    )


@teams_router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, session: SessionDep, user: CurrentUser):
    await svc_teams.delete_team(session, actor=user, team_id=team_id)
    return None
