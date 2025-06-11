from datetime import datetime
from dataclasses import dataclass, field
from domain.entities.user import MixinId, MixinDate

@dataclass
class ExpenseEdit:
    id: int
    amount: float
    category_id: int
    note: str

@dataclass
class ExpenseCreate:
    user_id: int
    amount: float
    category_id: int
    note: str
    id: int | None = field(default=None)

@dataclass
class ExpenseInDB(MixinId, MixinDate, ExpenseCreate):
    ...

@dataclass
class ExpenseHistoryPeriod:
    user_id: int
    period: str # "day" | "week" | "month" | "year"

@dataclass
class ExpenseHistory(ExpenseHistoryPeriod):
    date: datetime
    category_name: str
    count: int
    total_amount: float
    # display_date: str
