from fastapi import APIRouter, Request, BackgroundTasks
from app.core.events_parser import PremisEvents
from app.core.event_handler import handle_event

router = APIRouter()


@router.post("/", status_code=202)
async def handle_events(request: Request, background_tasks: BackgroundTasks):
    """
    Returns OK if the xml parsing didn't crash.
    """
    events_xml: bytes = await request.body()

    events = PremisEvents(events_xml).events

    for event in events:
        background_tasks.add_task(handle_event, event)

    return {"message": f"Updating {len(events)} item(s) with metadata from the original fragment in the background."}
