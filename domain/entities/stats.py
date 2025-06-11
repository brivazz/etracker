from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class StatsInDb:
    category_name: str
    total_amount: float

@dataclass
class StatsPeriodSummary:
    stats: list[StatsInDb]
    from_date: datetime
    to_date: datetime
