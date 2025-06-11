from datetime import datetime, timezone
from dataclasses import dataclass, field

@dataclass
class MixinId:
    id: int = field(default=0)

@dataclass
class MixinDate:
    created_at: datetime = field(default=datetime.now(timezone.utc))
    updated_at: datetime = field(default=datetime.now(timezone.utc))

@dataclass
class UserID(MixinId): ...

@dataclass
class UserCreate:
    username: str = field(default='')
    balance: float = field(default=0.0)
    telegram_id: int =field(default=0)

    # def top_up(self, amount: float):
    #     if amount <= 0:
    #         raise ValueError("Amount must be positive")
    #     self.balance += amount

@dataclass
class UserInDB(MixinId, MixinDate, UserCreate):
    user_id: int = field(default=0)

# @dataclass
# class UserSettings(MixinId, MixinDate):
#     user_id: int = field(default_factory=int)
#     default_category: str = field(default_factory=str)

@dataclass
class UserIdPeriod:
    user_id: int
    period: str  # 'day', 'week', 'month', 'year'

