import logging
from typing import Any, Dict, List

from wrangler.constants import PLATE_PURPOSE_ENTITY, PLATE_PURPOSE_STOCK, STUDY_ENTITY, STUDY_HERON
from wrangler.helpers.general_helpers import get_entity_uuid

logger = logging.getLogger(__name__)


def create_plate_body(plate_barcode: str, mlwh_results: List[Dict[str, str]]) -> Dict[str, Any]:
    wells_content = {}
    for sample in mlwh_results:
        well = {
            "supplier_name": sample["supplier_sample_id"],
        }
        wells_content[sample["coordinate"]] = well

    body = {
        "barcode": plate_barcode,
        "plate_purpose_uuid": get_entity_uuid(PLATE_PURPOSE_ENTITY, PLATE_PURPOSE_STOCK),
        "study_uuid": get_entity_uuid(STUDY_ENTITY, STUDY_HERON),
        "wells_content": wells_content,
    }

    return {"data": {"type": "plates", "attributes": body}}
