from datetime import datetime
from pydantic import BaseModel, Field


class CategoryCreateDTO(BaseModel):
    user_id: int
    name: str


class CategoryInDBDTO(CategoryCreateDTO):
    id: int | None = Field(default=None)
    created_at: datetime
    updated_at: datetime
