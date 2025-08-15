from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from .access_token import AccessToken, get_access_token_db
from app.auth.manager import get_user_manager
from app.core.config import settings
from app.models.user import User

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
