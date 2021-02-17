from app.core.events_parser import PremisEvent
from app.services.mediahaven import MediahavenService
from app.core.xml_transformer import transform_mh_result_to_sidecar
from viaa.configuration import ConfigParser
import asyncio


async def handle_event(premis_event: PremisEvent) -> None:
    config = ConfigParser().app_cfg
    mediahaven_service = MediahavenService(config)

    # Get metadata for the newly archived item
    fragment = mediahaven_service.get_fragment(premis_event.fragment_id)
    original_pid = fragment["Dynamic"]["dc_source"].split(".")[0]

    # Query mediahaven for the original item using PID
    original_metadata = mediahaven_service.query([("PID", original_pid)])

    # Transform the metadata to a new sidecar
    sidecar = transform_mh_result_to_sidecar(original_metadata)

    print(sidecar)
    # Update the newly archived item
