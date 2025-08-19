from typing import List

from fastapi import APIRouter, status

from app.core.dependencies import SessionDep, CurrentUser
from app.crud import workers as crud_workers
from app.schemas.members import MemberIn, MemberRead, MemberUpdate
from app.services import members as members_services
from app.utils import team_utils


members_router = APIRouter(prefix="/members", tags=["members"])


@members_router.get("/{team_id}/members", response_model=List[MemberRead])
async def list_members(team_id: int, session: SessionDep, user: CurrentUser):
    if not await team_utils.is_superuser(user):
        await team_utils.require_member(session, user.id, team_id)
    return await crud_workers.list_by_team(session, team_id)


@members_router.post("/{team_id}/members", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(team_id: int, body: MemberIn, session: SessionDep, user: CurrentUser):
    return await members_services.add_member(
        session, actor=user, team_id=team_id, user_id=body.user_id, role=body.role
    )


@members_router.patch("/{team_id}/members/{user_id}", response_model=MemberRead)
async def change_member_role(team_id: int, user_id: int, body: MemberUpdate, session: SessionDep, user: CurrentUser):
    return await members_services.change_member_role(
        session, actor=user, team_id=team_id, user_id=user_id, role=body.role
    )


@members_router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(team_id: int, user_id: int, session: SessionDep, user: CurrentUser):
    await members_services.remove_member(session, actor=user, team_id=team_id, user_id=user_id)
    return None
