from fastapi import APIRouter, Request
from app.core.events_parser import PremisEvents

router = APIRouter()


@router.post("/")
async def handle_events(request: Request):
    """
    Returns OK if the xml parsing didn't crash.
    """
    events_xml: bytes = await request.body()

    events = PremisEvents(events_xml)

    return "OK"
