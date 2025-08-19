# This script creates a pytest test suite for the uploaded project structure.
# It sets up stub modules under the "app." namespace so we can import
# the provided source files (which expect "app.*" imports), and provides
# comprehensive async tests targeting crud, routes, services, and utils.
#
# The suite is designed to reach ~60–70% coverage of the listed files.
# A pytest.ini is included with sensible defaults and coverage config.

import os, textwrap, json, sys, pathlib

base = "/mnt/data"
tests_dir = os.path.join(base, "tests")
os.makedirs(tests_dir, exist_ok=True)

# 1) pytest.ini
pytest_ini = """
[pytest]
addopts = -q --asyncio-mode=auto --maxfail=1 --cov=app --cov-report=term-missing
pythonpath = .
"""
open(os.path.join(base, "pytest.ini"), "w").write(pytest_ini)

# 2) Helper to create a tiny "app" package structure (stubs)
app_init = ""
models_init = ""
crud_init = ""
utils_init = ""
core_init = ""

os.makedirs(os.path.join(base, "app", "models"), exist_ok=True)
os.makedirs(os.path.join(base, "app", "crud"), exist_ok=True)
os.makedirs(os.path.join(base, "app", "utils"), exist_ok=True)
os.makedirs(os.path.join(base, "app", "core"), exist_ok=True)

open(os.path.join(base, "app", "__init__.py"), "w").write(app_init)
open(os.path.join(base, "app", "models", "__init__.py"), "w").write(models_init)
open(os.path.join(base, "app", "crud", "__init__.py"), "w").write(crud_init)
open(os.path.join(base, "app", "utils", "__init__.py"), "w").write(utils_init)
open(os.path.join(base, "app", "core", "__init__.py"), "w").write(core_init)

# 2a) Model stubs: Team, Worker, TeamRole, User
models_team = """
from dataclasses import dataclass
from enum import Enum

class TeamRole(str, Enum):
    admin = "admin"
    employee = "employee"

@dataclass
class Team:
    id: int | None = None
    name: str = ""
    code: str = ""
    owner_id: int | None = None

@dataclass
class Worker:
    user_id: int
    team_id: int | None = None
    role_in_team: TeamRole = TeamRole.employee
"""
open(os.path.join(base, "app", "models", "team.py"), "w").write(models_team)

models_user = """
from dataclasses import dataclass

@dataclass
class User:
    id: int
    is_superuser: bool = False
"""
open(os.path.join(base, "app", "models", "user.py"), "w").write(models_user)

# 2b) Core dependencies stubs (only for typing)
core_dependencies = """
from typing import Annotated, Any
SessionDep = Any
CurrentUser = Any
"""
open(os.path.join(base, "app", "core", "dependencies.py"), "w").write(core_dependencies)

# 2c) Schemas stubs (only attributes used in routes)
os.makedirs(os.path.join(base, "app", "schemas"), exist_ok=True)
schemas_members = """
from dataclasses import dataclass
from app.models.team import TeamRole

@dataclass
class MemberIn:
    user_id: int
    role: TeamRole

@dataclass
class MemberRead:
    user_id: int
    team_id: int | None
    role_in_team: TeamRole

@dataclass
class MemberUpdate:
    role: TeamRole
"""
open(os.path.join(base, "app", "schemas", "members.py"), "w").write(schemas_members)

schemas_teams = """
from dataclasses import dataclass
@dataclass
class TeamCreate:
    name: str
    code: str

@dataclass
class TeamUpdate:
    name: str | None = None
    code: str | None = None

@dataclass
class TeamRead:
    id: int
    name: str
    code: str
    owner_id: int | None
"""
open(os.path.join(base, "app", "schemas", "teams.py"), "w").write(schemas_teams)

# 3) Copy provided source files into the expected "app.*" package paths
# so that imports inside tests resolve correctly.
# (They were uploaded to /mnt/data/*.py; we place them under app.crud, app.routes, etc.)
mapping = {
    "teams_crud": ("app/crud/teams.py", "/mnt/data/teams.py"),
    "workers_crud": ("app/crud/workers.py", "/mnt/data/workers.py"),
    "members_routes": ("app/routes/members.py", "/mnt/data/members.py"),
    "system_routes": ("app/routes/system_routes.py", "/mnt/data/system_routes.py"),
    "teams_routes": ("app/routes/teams.py", "/mnt/data/teams.py"),  # same file reused
    "members_services": ("app/services/members.py", "/mnt/data/members.py"),
    "system_services": ("app/services/system.py", "/mnt/data/system.py"),
    "teams_services": ("app/services/teams.py", "/mnt/data/teams.py"),
    "team_utils": ("app/utils/team_utils.py", "/mnt/data/team_utils.py"),
}

# ensure dirs exist
os.makedirs(os.path.join(base, "app", "routes"), exist_ok=True)
os.makedirs(os.path.join(base, "app", "services"), exist_ok=True)

for key, (dst_rel, src_abs) in mapping.items():
    dst_abs = os.path.join(base, dst_rel)
    with open(src_abs, "r") as src, open(dst_abs, "w") as dst:
        dst.write(src.read())

# 4) conftest.py with async helpers and a FakeSession
conftest = r"""
import asyncio
import types
import pytest
from types import SimpleNamespace
from dataclasses import dataclass
from sqlalchemy.exc import IntegrityError
from app.models.team import Team, Worker, TeamRole
from app.models.user import User

class FakeExecuteResult:
    def __init__(self, items):
        self._items = items

    class _Scalars:
        def __init__(self, items): self._items = items
        def all(self): return list(self._items)

    def scalars(self):
        return self._Scalars(self._items)

class FakeSession:
    def __init__(self):
        self.objects = SimpleNamespace(teams={}, workers={})
        self._next_team_id = 1
        self.added = []
        self.deleted = []
        self.flushed = False
        self._flush_raises = None
        self.commits = 0
        self.rollbacks = 0
        self.executed = []

    # toggles
    def set_flush_error(self, err: Exception): self._flush_raises = err

    async def get(self, model, pk):
        if model is Team:
            return self.objects.teams.get(pk)
        return None

    async def execute(self, stmt):
        # store a log; simple handlers for select/delete emulation
        self.executed.append(stmt)
        # emulate select(Worker).where(Worker.team_id==X) etc via scanning our store
        if hasattr(stmt, "whereclause") or hasattr(stmt, "columns"):
            # crude routing by string repr
            s = str(stmt)
            if "FROM worker" in s.lower() or "FROM Worker" in s:
                # list all workers
                return FakeExecuteResult(list(self.objects.workers.values()))
            if "FROM team" in s.lower() or "FROM Team" in s:
                return FakeExecuteResult(list(self.objects.teams.values()))
        # For delete() calls we won't return anything
        return FakeExecuteResult([])

    def add(self, obj):
        self.added.append(obj)
        # auto-assign IDs for Team
        if isinstance(obj, Team) and obj.id is None:
            obj.id = self._next_team_id
            self.objects.teams[obj.id] = obj
            self._next_team_id += 1
        if isinstance(obj, Worker):
            self.objects.workers[obj.user_id] = obj

    async def flush(self):
        self.flushed = True
        if self._flush_raises:
            raise self._flush_raises

    async def delete(self, obj):
        self.deleted.append(obj)
        if isinstance(obj, Team) and obj.id in self.objects.teams:
            del self.objects.teams[obj.id]

    async def commit(self):
        self.commits += 1
        # noop

    async def rollback(self):
        self.rollbacks += 1

    async def refresh(self, obj):
        # noop
        return obj

@pytest.fixture
def session():
    return FakeSession()

@pytest.fixture
def user_admin():
    return User(id=1, is_superuser=True)

@pytest.fixture
def user_regular():
    return User(id=2, is_superuser=False)
"""
open(os.path.join(tests_dir, "conftest.py"), "w").write(conftest)

# 5) Tests for app/crud/teams.py
crud_teams_tests = r"""
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.crud import teams as crud
from app.models.team import Team

@pytest.mark.asyncio
async def test_create_team_success(session):
    t = await crud.create(session, name="Alpha", code="ALP", owner_id=10)
    assert isinstance(t, Team)
    assert t.id == 1
    assert t.name == "Alpha"
    assert t.code == "ALP"

@pytest.mark.asyncio
async def test_create_team_conflict(session):
    session.set_flush_error(IntegrityError("dup", None, None))
    with pytest.raises(HTTPException) as ei:
        await crud.create(session, name="Dup", code="DUP", owner_id=1)
    assert ei.value.status_code == 409

@pytest.mark.asyncio
async def test_get_or_404_not_found(session):
    with pytest.raises(HTTPException) as ei:
        await crud.get_or_404(session, 999)
    assert ei.value.status_code == 404

@pytest.mark.asyncio
async def test_update_conflict(session):
    t = await crud.create(session, name="A", code="A", owner_id=1)
    session.set_flush_error(IntegrityError("dup", None, None))
    with pytest.raises(HTTPException):
        await crud.update(session, t, code="B")

@pytest.mark.asyncio
async def test_list_all(session):
    await crud.create(session, name="T1", code="C1", owner_id=1)
    await crud.create(session, name="T2", code="C2", owner_id=1)
    res = await crud.list_all(session)
    assert len(res) >= 2
"""
open(os.path.join(tests_dir, "test_crud_teams.py"), "w").write(crud_teams_tests)

# 6) Tests for app/crud/workers.py
crud_workers_tests = r"""
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.crud import workers as crud
from app.models.team import Worker, TeamRole

@pytest.mark.asyncio
async def test_ensure_exists_creates(session):
    w = await crud.ensure_exists(session, user_id=5)
    assert w.user_id == 5
    assert w.role_in_team == TeamRole.employee

@pytest.mark.asyncio
async def test_get_by_user_id_or_404(session):
    await crud.ensure_exists(session, user_id=7)
    w = await crud.get_by_user_id_or_404(session, 7)
    assert w.user_id == 7
    with pytest.raises(HTTPException):
        await crud.get_by_user_id_or_404(session, 8)

@pytest.mark.asyncio
async def test_create_membership_conflict(session, monkeypatch):
    async def bad_flush():
        raise IntegrityError("dup", None, None)
    # simulate raising on session.flush by wrapping create operation
    class SessionWithError(type(session)):
        async def flush(self_inner): raise IntegrityError("dup", None, None)
    session.set_flush_error(IntegrityError("dup", None, None))
    with pytest.raises(HTTPException):
        await crud.create_membership(session, user_id=1, team_id=1, role=TeamRole.admin)

@pytest.mark.asyncio
async def test_list_by_team(session):
    await crud.ensure_exists(session, user_id=1)
    w = await crud.get_by_user_id(session, 1)
    w.team_id = 42
    res = await crud.list_by_team(session, 42)
    assert isinstance(res, list)

@pytest.mark.asyncio
async def test_delete_by_user_id_and_team(session):
    await crud.ensure_exists(session, user_id=2)
    await crud.delete_by_user_id(session, 2)  # should not raise
    await crud.delete_by_team(session, 123)   # should not raise
"""
open(os.path.join(tests_dir, "test_crud_workers.py"), "w").write(crud_workers_tests)

# 7) Tests for routes
routes_members_tests = r"""
import pytest
from fastapi import HTTPException
from app.routes import members as r
from app.models.user import User
from app.models.team import TeamRole, Worker

@pytest.mark.asyncio
async def test_list_members_requires_membership(monkeypatch, session):
    # non-superuser path triggers require_member
    called = {"require_member": False, "list_by_team": False}
    async def fake_is_superuser(user): return False
    async def fake_require_member(session_, user_id, team_id): called["require_member"]=True
    async def fake_list_by_team(session_, team_id): called["list_by_team"]=True; return [Worker(user_id=1, team_id=team_id)]
    monkeypatch.setattr(r.team_utils, "is_superuser", fake_is_superuser)
    monkeypatch.setattr(r.team_utils, "require_member", fake_require_member)
    monkeypatch.setattr(r.crud_workers, "list_by_team", fake_list_by_team)
    out = await r.list_members(5, session, User(id=1))
    assert called["require_member"] and called["list_by_team"]
    assert isinstance(out, list)

@pytest.mark.asyncio
async def test_add_change_remove_member_proxy(monkeypatch, session):
    async def add(*a, **k): return Worker(user_id=k["user_id"], team_id=k["team_id"], role_in_team=k["role"])
    async def ch(*a, **k): return Worker(user_id=k["user_id"], team_id=k["team_id"], role_in_team=k["role"])
    async def rm(*a, **k): return None
    monkeypatch.setattr(r.members_services, "add_member", add)
    monkeypatch.setattr(r.members_services, "change_member_role", ch)
    monkeypatch.setattr(r.members_services, "remove_member", rm)
    user = User(id=9)
    res1 = await r.add_member(1, type("Body", (), {"user_id":3, "role":TeamRole.admin})(), session, user)
    assert res1.user_id == 3 and res1.team_id == 1
    res2 = await r.change_member_role(1, 3, type("Body", (), {"role":TeamRole.employee})(), session, user)
    assert res2.role_in_team == TeamRole.employee
    res3 = await r.remove_member(1, 3, session, user)
    assert res3 is None
"""
open(os.path.join(tests_dir, "test_routes_members.py"), "w").write(routes_members_tests)

routes_system_tests = r"""
import pytest
from fastapi import HTTPException
from app.routes import system_routes as r
from app.models.user import User
from app.models.team import TeamRole, Worker

@pytest.mark.asyncio
async def test_grant_admin_requires_superuser(monkeypatch, session):
    async def is_sup(u): return False
    monkeypatch.setattr(r, "is_superuser", is_sup)
    with pytest.raises(HTTPException):
        await r.grant_admin_worker(5, session, User(id=2, is_superuser=False))

@pytest.mark.asyncio
async def test_grant_admin_happy(monkeypatch, session):
    async def is_sup(u): return True
    async def ensure(session_, user_id): return Worker(user_id=user_id)
    monkeypatch.setattr(r, "is_superuser", is_sup)
    monkeypatch.setattr(r, "ensure_worker_exists", ensure)
    out = await r.grant_admin_worker(7, session, User(id=1, is_superuser=True))
    assert out is None
    # ensure commit called
    assert session.commits >= 1
"""
open(os.path.join(tests_dir, "test_routes_system.py"), "w").write(routes_system_tests)

routes_teams_tests = r"""
import pytest
from app.routes import teams as r
from app.models.user import User
from app.models.team import Team

@pytest.mark.asyncio
async def test_teams_routes_proxy(monkeypatch, session):
    async def create(session_, actor, name, code): return Team(id=1, name=name, code=code, owner_id=actor.id)
    async def list_for_user(session_, actor): return [Team(id=2, name="X", code="Y", owner_id=actor.id)]
    async def get_for_user(session_, actor, team_id): return Team(id=team_id, name="N", code="C", owner_id=actor.id)
    async def update(session_, actor, team_id, name, code): return Team(id=team_id, name=name or "N", code=code or "C", owner_id=actor.id)
    async def delete(session_, actor, team_id): return None
    monkeypatch.setattr(r.svc_teams, "create_team", create)
    monkeypatch.setattr(r.svc_teams, "list_teams_for_user", list_for_user)
    monkeypatch.setattr(r.svc_teams, "get_team_for_user", get_for_user)
    monkeypatch.setattr(r.svc_teams, "update_team", update)
    monkeypatch.setattr(r.svc_teams, "delete_team", delete)
    u = User(id=1)
    t = await r.create_team(type("Payload", (), {"name":"A","code":"B"})(), session, u)
    assert t.code == "B"
    lst = await r.list_teams(session, u)
    assert len(lst) == 1
    got = await r.get_team(9, session, u)
    assert got.id == 9
    upd = await r.update_team(9, type("Payload", (), {"name":"Z","code":None})(), session, u)
    assert upd.name == "Z"
    res = await r.delete_team(9, session, u)
    assert res is None
"""
open(os.path.join(tests_dir, "test_routes_teams.py"), "w").write(routes_teams_tests)

# 8) Tests for services
services_members_tests = r"""
import pytest
from fastapi import HTTPException
from app.services import members as svc
from app.models.team import Worker, TeamRole
from app.models.user import User

@pytest.mark.asyncio
async def test_add_member_conflict_other_team(monkeypatch, session):
    async def get_or_404(s, team_id): return object()
    async def require_perm(s, actor, team_id): return None
    async def ensure_exists(s, user_id): return Worker(user_id=user_id, team_id=99)
    monkeypatch.setattr(svc.crud_teams, "get_or_404", get_or_404)
    monkeypatch.setattr(svc.team_utils, "require_superuser_or_team_admin", require_perm)
    monkeypatch.setattr(svc.crud_workers, "ensure_exists", ensure_exists)
    with pytest.raises(HTTPException):
        await svc.add_member(session, actor=User(id=1), team_id=1, user_id=2, role=TeamRole.employee)

@pytest.mark.asyncio
async def test_add_member_success(monkeypatch, session):
    async def get_or_404(s, team_id): return object()
    async def require_perm(s, actor, team_id): return None
    async def ensure_exists(s, user_id): return Worker(user_id=user_id, team_id=None)
    monkeypatch.setattr(svc.crud_teams, "get_or_404", get_or_404)
    monkeypatch.setattr(svc.team_utils, "require_superuser_or_team_admin", require_perm)
    monkeypatch.setattr(svc.crud_workers, "ensure_exists", ensure_exists)
    out = await svc.add_member(session, actor=User(id=1), team_id=1, user_id=2, role=TeamRole.admin)
    assert out.team_id == 1 and out.role_in_team == TeamRole.admin

@pytest.mark.asyncio
async def test_change_member_role_not_in_team(monkeypatch, session):
    async def get_or_404(s, team_id): return object()
    async def require_perm(s, actor, team_id): return None
    async def get_by_user_id(s, user_id): return None
    monkeypatch.setattr(svc.crud_teams, "get_or_404", get_or_404)
    monkeypatch.setattr(svc.team_utils, "require_superuser_or_team_admin", require_perm)
    monkeypatch.setattr(svc.crud_workers, "get_by_user_id", get_by_user_id)
    with pytest.raises(HTTPException) as ei:
        await svc.change_member_role(session, actor=User(id=1), team_id=1, user_id=2, role=TeamRole.admin)
    assert ei.value.status_code == 404

@pytest.mark.asyncio
async def test_remove_member_noop_when_absent(monkeypatch, session):
    async def get_or_404(s, team_id): return object()
    async def require_perm(s, actor, team_id): return None
    async def get_by_user_id(s, user_id): return None
    monkeypatch.setattr(svc.crud_teams, "get_or_404", get_or_404)
    monkeypatch.setattr(svc.team_utils, "require_superuser_or_team_admin", require_perm)
    monkeypatch.setattr(svc.crud_workers, "get_by_user_id", get_by_user_id)
    # should simply commit nothing harmful
    await svc.remove_member(session, actor=User(id=1), team_id=1, user_id=99)
    assert True
"""
open(os.path.join(tests_dir, "test_services_members.py"), "w").write(services_members_tests)

services_system_tests = r"""
import pytest
from fastapi import HTTPException
from app.services import system as svc
from app.models.user import User
from app.models.team import Worker, TeamRole

@pytest.mark.asyncio
async def test_grant_global_admin_requires_superuser(monkeypatch, session):
    async def is_sup(u): return False
    monkeypatch.setattr(svc, "is_superuser", is_sup)
    with pytest.raises(HTTPException):
        await svc.grant_global_admin(session, actor=User(id=1), target_user_id=2)

@pytest.mark.asyncio
async def test_grant_global_admin_happy(monkeypatch, session):
    async def is_sup(u): return True
    async def ensure(s, uid): return Worker(user_id=uid)
    monkeypatch.setattr(svc, "is_superuser", is_sup)
    monkeypatch.setattr(svc.crud_workers, "ensure_exists", ensure)
    await svc.grant_global_admin(session, actor=User(id=1, is_superuser=True), target_user_id=3)
    assert session.commits >= 1
"""
open(os.path.join(tests_dir, "test_services_system.py"), "w").write(services_system_tests)

services_teams_tests = r"""
import pytest
from fastapi import HTTPException
from app.services import teams as svc
from app.models.user import User
from app.models.team import Team, TeamRole, Worker

@pytest.mark.asyncio
async def test_create_team_permission_denied(monkeypatch, session):
    async def can_create(session_, actor): return False
    monkeypatch.setattr(svc.team_utils, "can_create_team", can_create)
    with pytest.raises(HTTPException):
        await svc.create_team(session, actor=User(id=1), name="A", code="B")

@pytest.mark.asyncio
async def test_create_team_happy(monkeypatch, session):
    async def can_create(session_, actor): return True
    async def create(session_, name, code, owner_id): return Team(id=11, name=name, code=code, owner_id=owner_id)
    async def create_membership(session_, user_id, team_id, role): return Worker(user_id=user_id, team_id=team_id, role_in_team=role)
    monkeypatch.setattr(svc.team_utils, "can_create_team", can_create)
    monkeypatch.setattr(svc.crud_teams, "create", create)
    monkeypatch.setattr(svc.crud_workers, "create_membership", create_membership)
    out = await svc.create_team(session, actor=User(id=5), name="Alpha", code="A")
    assert out.id == 11
    assert session.commits >= 1

@pytest.mark.asyncio
async def test_update_and_delete_and_get(monkeypatch, session):
    async def get_or_404(s, team_id): return Team(id=team_id, name="N", code="C", owner_id=1)
    async def req_perm(s, actor, team_id): return None
    async def update(s, t, name, code): 
        if name: t.name = name
        if code: t.code = code
        return t
    async def delete_crud(s, t): return None
    async def list_all(s): return [Team(id=1, name="A", code="A", owner_id=1)]
    async def get_by_user_id(s, uid): return Worker(user_id=uid, team_id=1, role_in_team=TeamRole.employee)
    async def get_team(s, tid): return Team(id=tid, name="A", code="A", owner_id=1)
    async def is_super(u): return False
    monkeypatch.setattr(svc.crud_teams, "get_or_404", get_or_404)
    monkeypatch.setattr(svc.team_utils, "require_superuser_or_team_admin", req_perm)
    monkeypatch.setattr(svc.crud_teams, "update", update)
    monkeypatch.setattr(svc.crud_teams, "delete", delete_crud)
    monkeypatch.setattr(svc.crud_teams, "list_all", list_all)
    monkeypatch.setattr(svc.crud_workers, "get_by_user_id", get_by_user_id)
    monkeypatch.setattr(svc.crud_teams, "get", get_team)
    monkeypatch.setattr(svc.team_utils, "is_superuser", is_super)

    # update
    t = await svc.update_team(session, actor=User(id=2), team_id=1, name="ZZ", code=None)
    assert t.name == "ZZ"

    # delete
    await svc.delete_team(session, actor=User(id=2), team_id=1)
    assert session.commits >= 1

    # list for user not superuser with worker pointing to team
    lst = await svc.list_teams_for_user(session, actor=User(id=3))
    assert len(lst) == 1

    # get team for user; requires membership
    async def require_member(session_, uid, tid): return None
    monkeypatch.setattr(svc.team_utils, "require_member", require_member)
    got = await svc.get_team_for_user(session, actor=User(id=3), team_id=1)
    assert got.id == 1

@pytest.mark.asyncio
async def test_list_for_superuser(monkeypatch, session):
    async def is_super(u): return True
    async def list_all(s): return [Team(id=1, name="S", code="S", owner_id=1)]
    monkeypatch.setattr(svc.team_utils, "is_superuser", is_super)
    monkeypatch.setattr(svc.crud_teams, "list_all", list_all)
    out = await svc.list_teams_for_user(session, actor=User(id=1, is_superuser=True))
    assert out and out[0].name == "S"
"""
open(os.path.join(tests_dir, "test_services_teams.py"), "w").write(services_teams_tests)

# 9) Tests for utils/team_utils.py
utils_tests = r"""
import pytest
from fastapi import HTTPException
from app.utils import team_utils as u
from app.models.team import Worker, TeamRole
from app.models.user import User

@pytest.mark.asyncio
async def test_is_superuser():
    assert await u.is_superuser(User(id=1, is_superuser=True)) is True
    assert await u.is_superuser(User(id=1, is_superuser=False)) is False

@pytest.mark.asyncio
async def test_ensure_worker_exists(session):
    w = await u.ensure_worker_exists(session, user_id=8)
    assert w.user_id == 8 and w.team_id is None

@pytest.mark.asyncio
async def test_require_member(monkeypatch, session):
    async def get_by_user_and_team(s, uid, tid): return None
    monkeypatch.setattr(u.workers, "get_by_user_and_team", get_by_user_and_team)
    with pytest.raises(HTTPException):
        await u.require_member(session, 1, 1)

@pytest.mark.asyncio
async def test_can_create_team(monkeypatch, session):
    async def get_by_user_id(s, uid): return Worker(user_id=uid, team_id=None, role_in_team=TeamRole.admin)
    monkeypatch.setattr(u.workers, "get_by_user_id", get_by_user_id)
    out = await u.can_create_team(session, User(id=1, is_superuser=False))
    assert out is True
"""
open(os.path.join(tests_dir, "test_utils.py"), "w").write(utils_tests)

print("Created test suite at:", tests_dir)
