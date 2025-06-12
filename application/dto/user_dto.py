from datetime import datetime
from pydantic import BaseModel


class UserIdDTO(BaseModel):
    user_id: int


class UserCreateDTO(BaseModel):
    username: str
    balance: float | int
    telegram_id: int


class UserInDBDTO(UserCreateDTO):
    id: int
    created_at: datetime
