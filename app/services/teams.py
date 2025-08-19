from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.team import Team, TeamRole
from app.crud import teams as crud_teams
from app.crud import workers as crud_workers
from app.utils import team_utils


async def create_team(session: AsyncSession, *, actor: User, name: str, code: str) -> Team:
    if not await team_utils.can_create_team(session, actor):
        raise HTTPException(status_code=403, detail="Only global admin or local admin can create teams")

    team = await crud_teams.create(session, name=name, code=code, owner_id=actor.id)

    # привязываем актёра к команде, если он был глобальным админом без команды
    await crud_workers.create_membership(session, user_id=actor.id, team_id=team.id, role=TeamRole.admin)
    await session.commit()
    await session.refresh(team)
    return team


async def update_team(session: AsyncSession, *, actor: User, team_id: int, name: str | None, code: str | None) -> Team:
    team = await crud_teams.get_or_404(session, team_id)
    await team_utils.require_superuser_or_team_admin(session, actor, team_id)
    team = await crud_teams.update(session, team, name=name, code=code)
    await session.commit()
    await session.refresh(team)
    return team


async def delete_team(session: AsyncSession, *, actor: User, team_id: int) -> None:
    team = await crud_teams.get_or_404(session, team_id)
    await team_utils.require_superuser_or_team_admin(session, actor, team_id)

    await crud_workers.delete_by_team(session, team_id)

    await crud_teams.delete(session, team)
    await session.commit()


async def list_teams_for_user(session: AsyncSession, *, actor: User) -> list[Team]:
    if await team_utils.is_superuser(actor):
        return await crud_teams.list_all(session)
    w = await crud_workers.get_by_user_id(session, actor.id)
    if not w or w.team_id is None:
        return []
    team = await crud_teams.get(session, w.team_id)
    return [team] if team else []


async def get_team_for_user(session: AsyncSession, *, actor: User, team_id: int) -> Team:
    team = await crud_teams.get_or_404(session, team_id)
    if not await team_utils.is_superuser(actor):
        await team_utils.require_member(session, actor.id, team_id)
    return team
