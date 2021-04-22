from app.core.xml_transformer import transform_mh_result_to_sidecar
from tests.resources import fragment_info_xml, sidecar


def test_handle_events() -> None:
    # ARRANGE

    # ACT
    transformed = transform_mh_result_to_sidecar(fragment_info_xml)
    # ASSERT
    assert transformed == sidecar
