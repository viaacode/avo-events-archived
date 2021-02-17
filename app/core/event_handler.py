from app.core.events_parser import PremisEvent
from app.services.mediahaven import MediahavenService
from viaa.configuration import ConfigParser
import asyncio


async def handle_event(premis_event: PremisEvent) -> None:
    config = ConfigParser().app_cfg
    mediahaven_service = MediahavenService(config)

    # Get metadata for the newly archived item
    fragment = mediahaven_service.get_fragment(premis_event.fragment_id)
    original_pid = fragment["Dynamic"]["dc_source"].split(".")[0]

    print(original_pid)
    # Query mediahaven for the original item using PID
    original_metadata = mediahaven_service.query([("PID", original_pid)])

    print(original_metadata.text)
    # Transform the metadata to a new sidecar

    # Update the newly archived item

