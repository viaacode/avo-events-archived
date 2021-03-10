from typing import List

from pydantic import BaseModel


class PremisEvent(BaseModel):
    event_type: str
    event_datetime: str
    event_detail: str
    event_id: str
    event_outcome: str
    mediahaven_id: str
    external_id: str
    is_valid: bool
    has_valid_outcome: bool


class PremisEvents(BaseModel):
    events: List[PremisEvent]
