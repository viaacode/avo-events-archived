from requests.exceptions import HTTPError
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.core.xml_transformer import transform_mh_result_to_sidecar
from app.models.premis_events import PremisEvent
from app.services.mediahaven import MediahavenService, MediaObjectNotFoundException

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


def determine_original_item(mediahaven_result: dict) -> str:
    """From a MediaHaven result list, determine which of the items carries the
    original metadata.

    A MediaHaven-query by pid can result in 0, 1 or more results. Depending on
    the "structure" of the resultset (ie., the relations between the different
    items) we need to choose either the main fragment or a real fragment.
    The - proposed - heuristic is:
    - if only one result, return
    - if more then one result: filter out `type=document` (ie., the collaterals)
        - if only one item left: return
        - if more then one item left: return main fragment

    Args:
        The MediaHaven resultset as dict
    Returns:
        The correct fragment ID as string, or an empty string if none found.
    """
    # Init `original_fragment_id` to the empty string (making the search
    # exhaustive and thus avoiding explicitly handling the case of an empty
    # resultset)
    original_fragment_id = ""
    # Simple case: if there is only one result, this is the one. No questions
    # asked.
    if mediahaven_result["TotalNrOfResults"] == 1:
        original_fragment_id = mediahaven_result["MediaDataList"][0]["Internal"]["FragmentId"]
    # If there are multiple items for the PID, we filter out the "documents"
    # and see what's left
    elif mediahaven_result["TotalNrOfResults"] > 1:
        records_minus_documents = [
            item for item in mediahaven_result["MediaDataList"] if not
            item["Administrative"]["Type"] == "document"
        ]
        # If there's only one record
        if len(records_minus_documents) == 1:
            original_fragment_id = records_minus_documents[0]["Internal"]["FragmentId"]
        # If there's more then one record left we pick the "main fragment",
        # regardless of it's type. (Theoretically, zero records could remain
        # if all were of type "document".)
        else:
            original_fragment_id = next(
                (item["Internal"]["FragmentId"] for
                item in records_minus_documents
                if not item["Internal"]["IsFragment"])
            )
    return original_fragment_id


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
        log.error(
            "Got a PREMIS event, but the mediahaven id is not in MediaHaven",
            mediahaven_id=premis_event.mediahaven_id,
            exception=str(e),
        )
        return

    fragment_id = fragment["Internal"]["FragmentId"]

    try:
        original_pid = fragment["Dynamic"]["s3_object_key"].split(".")[0]
    except KeyError as e:
        log.warning(
            f"{e} is missing on the testbeeld item.",
            mediahaven_id=premis_event.mediahaven_id,
        )
        return

    # Query mediahaven for the original item using PID
    try:
        result = mediahaven_service.query([("PID", original_pid)])
    except HTTPError as e:
        log.warning(
            "Something went wrong querying Mediahaven for the original item.",
            mediahaven_id=premis_event.mediahaven_id,
            original_pid=original_pid,
            exception=str(e),
        )
        return

    # Determine the correct fragment ID from the result
    original_fragment_id = determine_original_item(result)

    if not original_fragment_id:
        log.warning(
            "No item found for original_pid.",
            mediahaven_id=premis_event.mediahaven_id,
            original_pid=original_pid,
        )
        return

    # Get the original metadata
    try:
        original_metadata = mediahaven_service.get_fragment(original_fragment_id, "xml")
    except HTTPError as e:
        log.warning(
            "Something went wrong while connecting to MH.",
            mediahaven_id=premis_event.mediahaven_id,
            fragment_id=fragment_id,
            original_pid=original_pid,
            original_fragment_id=original_fragment_id,
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
