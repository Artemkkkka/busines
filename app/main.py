from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api.v1.routes import router as api_v1_router
from app.db.session import get_session

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
