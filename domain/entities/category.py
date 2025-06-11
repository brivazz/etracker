from dataclasses import dataclass, field
from domain.entities.user import MixinId, MixinDate

@dataclass
class CategoryCreate:
    user_id: int
    name: str

@dataclass
class CategoryInDb(MixinId, MixinDate, CategoryCreate):
    ...
