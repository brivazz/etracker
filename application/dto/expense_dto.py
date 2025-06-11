from datetime import datetime
from pydantic import BaseModel, Field

class ExpenseCreateDTO(BaseModel):
    id: int | None = None
    user_id: int
    amount: float
    category_id: int
    note: str

class ExpenseInDBDTO(ExpenseCreateDTO):
    id: int | None = Field(default=None)
    category_name: str | None = Field(default=None)
    created_at: datetime
    updated_at: datetime

class ExpenseEditDTO(BaseModel):
    id: int
    amount: float
    category_id: int
    note: str

class ExpenseDeleteDTO(BaseModel):
    id: int


class ExpenseHistoryPeriodDTO(BaseModel):
    user_id: int
    period: str

class ExpenseHistoryDTO(ExpenseHistoryPeriodDTO):
    date: datetime
    category_name: str
    count: int
    total_amount: float
    # display_date: str
