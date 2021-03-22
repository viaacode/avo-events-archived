from fastapi import APIRouter, BackgroundTasks, Depends
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.core.event_handler import handle_event
from app.core.events_parser import parse_premis_events
from app.models.premis_events import PremisEvents
from app.models.xml_body import XmlBody

router = APIRouter()

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


@router.post("/", status_code=202)
async def handle_events(
    background_tasks: BackgroundTasks,
    premis_events: PremisEvents = Depends(XmlBody(PremisEvents, parse_premis_events)),
):
    """
    Returns OK if the xml parsing didn't crash.
    """
    events = premis_events.events

    archived_events = [
        event for event in events if event.is_valid and event.has_valid_outcome
    ]

    log.info(
        f"Got {len(events)} PREMIS-event(s) of which {len(archived_events)} archived-events(s) with outcome OK."
    )

    for event in events:
        background_tasks.add_task(handle_event, event)

    return {
        "message": f"Updating {len(events)} item(s) with metadata from the original fragment in the background."
    }
