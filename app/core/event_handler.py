from viaa.configuration import ConfigParser

from app.core.events_parser import PremisEvent
from app.core.xml_transformer import transform_mh_result_to_sidecar
from app.services.mediahaven import MediahavenService


async def handle_event(premis_event: PremisEvent) -> None:
    config = ConfigParser().app_cfg
    mediahaven_service = MediahavenService(config)
    fragment_id = premis_event.fragment_id

    # Get metadata for the newly archived item
    fragment = mediahaven_service.get_fragment(fragment_id)
    original_pid = fragment["Dynamic"]["s3_object_key"].split(".")[0]

    # Query mediahaven for the original item using PID
    original_metadata = mediahaven_service.query([("PID", original_pid)])

    # Transform the metadata to a new sidecar
    sidecar = transform_mh_result_to_sidecar(original_metadata)

    # Update the newly archived item
    is_update_successful = mediahaven_service.update_metadata(fragment_id, sidecar)

    if is_update_successful:
        print("WOOP WOOP, it worked")
    else:
        print("RIP")
