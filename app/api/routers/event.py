from fastapi import APIRouter, BackgroundTasks, Depends
from viaa.configuration import ConfigParser
from viaa.observability import logging
from mediahaven import MediaHaven

from app.core.event_handler import handle_event
from app.core.events_parser import parse_premis_events
from app.models.premis_events import PremisEvents
from app.models.xml_body import XmlBody

router = APIRouter()

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


def get_mediahaven_client():
    from app.app import _mediahaven_client

    return _mediahaven_client


@router.post("/", status_code=202)
async def handle_events(
    background_tasks: BackgroundTasks,
    premis_events: PremisEvents = Depends(XmlBody(PremisEvents, parse_premis_events)),
    mh_client: MediaHaven = Depends(get_mediahaven_client),
):
    """
    Returns OK if the xml parsing didn't crash.
    """
    events = premis_events.events

    archived_events = [
        event for event in events if event.is_valid and event.has_valid_outcome
    ]

    log.debug(
        f"Got {len(events)} PREMIS-event(s) of which {len(archived_events)} archived-event(s) with outcome OK."
    )

    for event in archived_events:
        background_tasks.add_task(handle_event, event, mh_client)

    return {
        "message": f"Updating {len(archived_events)} item(s) with metadata from the original fragment in the background."
    }
