from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
from bson import ObjectId


@dataclass
class Competition:
    _id: Optional[ObjectId] = ObjectId()
    message_id: Optional[str] = None
    is_active: Optional[bool] = None
    thumbnail_url: Optional[str] = None,
    name: Optional[str] = None,
    wom_id: Optional[int] = None,
    ends_on: Optional[datetime] = None,

    @classmethod
    def from_dict(cls, data: dict) -> "Competition":
        if data is None:
            return
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)
