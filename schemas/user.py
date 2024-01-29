from datetime import datetime

from pydantic import BaseModel

from common.enums import UserRole


class UserCreate(BaseModel):
    username: str
    role: UserRole


class UserResponse(UserCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
