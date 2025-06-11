from dataclasses import dataclass, field
from domain.entities.user import MixinId, MixinDate


@dataclass
class MessageCreate(MixinId, MixinDate):
    user_id: int = field(default_factory=int)
    text: str = field(default_factory=str)
    # amount:

@dataclass
class MessageInDB(MixinId, MixinDate):
    user_id: int = field(default_factory=int)
    text: str = field(default_factory=str)
