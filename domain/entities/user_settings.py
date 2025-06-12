from dataclasses import dataclass
from domain.entities.user import MixinId, MixinDate


@dataclass
class UserSettingsCreate:
    user_id: int
    default_category: str


@dataclass
class UserSettingsInDB(MixinId, MixinDate, UserSettingsCreate): ...
