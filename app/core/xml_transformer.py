import os

from lxml import etree


def transform_mh_result_to_sidecar(mh_result: bytes) -> bytes:
    xslt_path = os.path.join(os.getcwd(), "app", "resources", "transform.xslt")
    dom = etree.XML(mh_result)
    transform = etree.XSLT(etree.parse(xslt_path))
    sidecar = transform(dom)

    return etree.tostring(
        sidecar, encoding="utf-8", pretty_print=True, xml_declaration=True
    )
