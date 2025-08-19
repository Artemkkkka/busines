from fastapi import APIRouter, FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.v1.routes import router as api_v1_router
from app.auth.actions.admin import router as admin_router
from app.auth.auth import fastapi_users, auth_backend, current_user
from app.auth.users_self_router import build_self_router
from app.auth.schemas import UserRead, UserCreate, UserAdminUpdate, UserSelfUpdate
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.routers.system_routes import sys_router
from app.routers.members import members_router
from app.routers.teams import teams_router


app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/web/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
async def db_check(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """)
    )
    tables = [row[0] for row in result.fetchall()]

    return {
        "db_status": "ok" if tables else "empty",
        "tables": tables
    }

app.include_router(api_v1_router, prefix="/api/v1")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    build_self_router(),
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserAdminUpdate),
    prefix="/admin/users",
    tags=["admin"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

users_me_delete_router = APIRouter()


@users_me_delete_router.delete("/users/me", tags=["users"])
async def delete_me(user: User = Depends(current_user)):
    user_manager = (await fastapi_users.get_user_manager().__anext__())
    await user_manager.delete(user)
    return {"status": "deleted"}

app.include_router(users_me_delete_router)
app.include_router(admin_router)
app.include_router(sys_router)
app.include_router(members_router)
app.include_router(teams_router)
