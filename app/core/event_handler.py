import re
from typing import Union

from mediahaven import MediaHaven
from mediahaven.mediahaven import MediaHavenException, AcceptFormat
from mediahaven.resources.base_resource import (
    MediaHavenSingleObjectJSON,
    MediaHavenPageObject,
)
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.core.xml_transformer import transform_mh_result_to_sidecar
from app.models.premis_events import PremisEvent

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


def determine_original_pid(s3_object_key: str) -> Union[str, None]:
    """From an `s3_object_key`, determine the original pid.

    For exported items, the "export name", and thus the `s3_object_key` by
    which the item is uploaded to S3 is `<original_pid>.<extension>`. This
    "original_pid" can have several forms:
        - 10 char alphanumeric lowercase string, or,
        - 10 char alphanumeric lowercase string followed by an underscore and a
          variant (eg. `mezanine`),
    As to be not too restrictive, we allow for some variation in the part that
    follows the underscore. The `pid` itself, however, should not deviate from
    a 10 char lowercase alphanum string.

    Args:
        The `s3_object_key` (or export name) as str

    Returns:
        The likely original PID as a string, or None
    """
    pattern = re.compile("^[a-z0-9]{10}_?[a-zA-Z]{0,12}")
    match_obj = pattern.match(s3_object_key)
    if match_obj:
        return match_obj.group()
    return None


def get_original_pid_from_fragment(fragment: MediaHavenSingleObjectJSON) -> str:
    """Retrieve the `s3_object_key` and determine the original pid from the
    whole of the fragment.

    Here, we can return both a KeyError (if the `s3_object_key` would not be
    present) or a ValueError (if the export name and thus the original pid is
    likely wrong).

    Args:
        The MediaHaven fragment/record as MediaHavenSingleObjectJSON

    Returns:
        The original PID as a string, or KeyError/ValueError

    Raises:
        KeyError: If `s3_object_key` is absent.
        ValueError: If the original pid has a wrong format.
    """
    # This will raise a AttributeError if `s3_object_key` is not present
    s3_object_key = fragment.Dynamic.s3_object_key
    #
    original_pid = determine_original_pid(s3_object_key)
    # If we get None back, raise a ValueError
    if not original_pid:
        raise ValueError(f'Could not determine valid pid from "{s3_object_key}"')
    # Else, return the string (original_pid)
    return original_pid


def determine_original_item(mediahaven_result: MediaHavenPageObject) -> str:
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
        The MediaHaven resultset as MediaHavenPageObject
    Returns:
        The correct fragment ID as string, or an empty string if none found.
    """
    # Init `original_fragment_id` to the empty string (making the search
    # exhaustive and thus avoiding explicitly handling the case of an empty
    # resultset)
    original_fragment_id = ""
    # Simple case: if there is only one result, this is the one. No questions
    # asked.
    if mediahaven_result.total_nr_of_results == 1:
        original_fragment_id = mediahaven_result[0].Internal.FragmentId
    # If there are multiple items for the PID, we filter out the "documents" 
    # and the record types without descriptive metadata.
    elif mediahaven_result.total_nr_of_results > 1:
        record_types_to_filter = ["Media", "NewspaperPage", "BibliographicPage"]
        filtered_records = [
            item
            for item in mediahaven_result
            if not item.Administrative.Type == "document"
            and not item.Administrative.RecordType in record_types_to_filter
        ]
        # If there's only one record
        if len(filtered_records) == 1:
            original_fragment_id = filtered_records[0].Internal.FragmentId
        # If there's more then one record left we pick the "main fragment",
        # regardless of it's type. (Theoretically, zero records could remain
        # if all were of type "document".)
        else:
            original_fragment_id = next(
                (
                    item.Internal.FragmentId
                    for item in filtered_records
                    if not item.Internal.IsFragment
                )
            )
    return original_fragment_id


def handle_event(
    premis_event: PremisEvent,
    mh_client: MediaHaven,
) -> None:
    log.debug(
        "Start handling of PREMIS event.",
        mediahaven_id=premis_event.mediahaven_id,
    )

    mediahaven_id = premis_event.mediahaven_id

    # Get metadata for the newly archived item
    try:
        fragment = mh_client.records.get(mediahaven_id)
    except MediaHavenException as e:
        if e.status_code == 404:
            log.error(
                "Got a PREMIS event, but the mediahaven id is not in MediaHaven",
                mediahaven_id=premis_event.mediahaven_id,
                exception=str(e),
            )
        else:
            log.error(
                "Error occurred when requesting a record",
                mediahaven_id=premis_event.mediahaven_id,
                exception=str(e),
            )
        return

    fragment_id = fragment.Internal.FragmentId

    try:
        original_pid = get_original_pid_from_fragment(fragment)
    except AttributeError as e:
        log.warning(
            f"{e} is missing on the testbeeld item.",
            mediahaven_id=premis_event.mediahaven_id,
        )
        return
    except ValueError as e:
        log.warning(
            f"ValueError: {e}",
            mediahaven_id=premis_event.mediahaven_id,
        )
        return

    # Query mediahaven for the original item using PID
    try:
        result = mh_client.records.search(q=f"+PID:{original_pid}")
    except MediaHavenException as e:
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
        original_metadata = mh_client.records.get(
            original_fragment_id, accept_format=AcceptFormat.XML
        ).single_result
    except MediaHavenException as e:
        log.warning(
            "Something went wrong while requesting original metadata",
            mediahaven_id=premis_event.mediahaven_id,
            fragment_id=fragment_id,
            original_pid=original_pid,
            original_fragment_id=original_fragment_id,
            exception=str(e),
        )
        return

    # Transform the metadata to a new sidecar
    try:
        sidecar = transform_mh_result_to_sidecar(original_metadata.encode("utf-8"))
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
        mh_client.records.update(
            fragment_id,
            metadata=sidecar,
            metadata_content_type=AcceptFormat.XML.value,
            reason="[avo-events-handler] Update item with original metadata",
        )
    except MediaHavenException as e:
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
