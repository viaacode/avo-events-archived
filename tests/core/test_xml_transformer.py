from app.core.xml_transformer import transform_mh_result_to_sidecar
from tests.resources import query_result_single_result, sidecar


def test_handle_events() -> None:
    # ARRANGE

    # ACT
    transformed = transform_mh_result_to_sidecar(query_result_single_result)
    # ASSERT
    assert transformed == sidecar
