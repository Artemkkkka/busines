from typing import Annotated, Optional
from pydantic import EmailStr, StringConstraints, ConfigDict

from fastapi_users import schemas

Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserRead(schemas.BaseUser[int]):
    global_role: str = "user"


class UserCreate(schemas.BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: Password

    def create_update_dict(self):
        data = self.model_dump(exclude_unset=True)
        data.update(
            {
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
            }
        )
        return data


class UserUpdate(schemas.BaseUserUpdate):
    global_role: Optional[str] = None
