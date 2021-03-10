from requests.exceptions import HTTPError
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.core.xml_transformer import transform_mh_result_to_sidecar
from app.models.premis_events import PremisEvent
from app.services.mediahaven import MediahavenService, MediaObjectNotFoundException

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


async def handle_event(premis_event: PremisEvent) -> None:
    log.debug(
        "Start handling of PREMIS event.",
        mediahaven_id=premis_event.mediahaven_id,
    )

    mediahaven_service = MediahavenService(config.app_cfg)
    mediahaven_id = premis_event.mediahaven_id

    # Get metadata for the newly archived item
    try:
        fragment = mediahaven_service.get_fragment(mediahaven_id)
    except MediaObjectNotFoundException as e:
        log.critical(
            "Got a PREMIS event, but the mediahaven id is not in MediaHaven",
            mediahaven_id=premis_event.mediahaven_id,
            exception=str(e),
        )
        return
    
    try:
        original_pid = fragment["Dynamic"]["s3_object_key"].split(".")[0]
        fragment_id = fragment["Internal"]["FragmentId"]
    except KeyError as e:
        log.warning(
            f"{e} is missing on the testbeeld item.",
            mediahaven_id=premis_event.mediahaven_id,
        )
        return

    # Query mediahaven for the original item using PID
    try:
        original_metadata = mediahaven_service.query([("PID", original_pid)])
    except HTTPError as e:
        log.warning(
            "Something went wrong querying Mediahaven for the original item.",
            mediahaven_id=premis_event.mediahaven_id,
            original_pid=original_pid,
            exception=str(e),
        )
        return

    # Transform the metadata to a new sidecar
    try:
        sidecar = transform_mh_result_to_sidecar(original_metadata)
    except Exception as e:
        log.warning(
            "Something went wrong transforming the original metadata.",
            mediahaven_id=premis_event.mediahaven_id,
            original_pid=original_pid,
            original_metadata=original_metadata,
            exception=str(e),
        )
        return

    # Update the newly archived item
    try:
        mediahaven_service.update_metadata(fragment_id, sidecar)
    except HTTPError as e:
        log.warning(
            "Something went wrong while update testbeeld item with original metadata.",
            mediahaven_id=premis_event.mediahaven_id,
            fragment_id=fragment_id,
            original_pid=original_pid,
            original_metadata=original_metadata,
            new_metadata=sidecar,
            exception=str(e),
        )
        return

    log.info(
        "Updated testbeeld item with original metadata.",
        fragment_id=fragment_id,
        mediahaven_id=mediahaven_id,
        original_pid=original_pid,
        new_metadata=sidecar,
    )
