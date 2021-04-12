from typing import List, Optional

from pydantic import BaseModel


class PremisEvent(BaseModel):
    event_type: str
    event_datetime: str
    event_detail: Optional[str]
    event_id: str
    event_outcome: str
    mediahaven_id: str
    external_id: str
    is_valid: bool
    has_valid_outcome: bool


class PremisEvents(BaseModel):
    events: List[PremisEvent]
