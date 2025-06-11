from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class StatsPeriodEnum(str, Enum):
    day = "day"
    week = "week"
    month = "month"

    def label(self) -> str:
        return {
            "day": "день",
            "week": "неделю",
            "month": "месяц"
        }[self.value]

class StatsRequestDTO(BaseModel):
    user_id: int
    period: StatsPeriodEnum

class StatsInDbDTO(BaseModel):
    category_name: str
    total_amount: float

class StatsPeriodDTO(BaseModel):
    stats: list[StatsInDbDTO]
    from_date: datetime
    to_date: datetime
