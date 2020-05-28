import logging
from typing import Any, Dict, List

from wrangler.constants import PLATE_PURPOSE_ENTITY, PLATE_PURPOSE_STOCK, STUDY_ENTITY, STUDY_HERON
from wrangler.helpers.general_helpers import get_entity_uuid
from wrangler.helpers.sample_helpers import sample_contents_for

logger = logging.getLogger(__name__)


def create_plate_body(plate_barcode: str, mlwh_results: List[Dict[str, str]]) -> Dict[str, Any]:
    wells_content = {}
    for sample in mlwh_results:
        wells_content[sample["position"]] = {
            "content": sample_contents_for(sample["supplier_sample_id"])
        }

    body = {
        "barcode": plate_barcode,
        "purpose_uuid": get_entity_uuid(PLATE_PURPOSE_ENTITY, PLATE_PURPOSE_STOCK),
        "study_uuid": get_entity_uuid(STUDY_ENTITY, STUDY_HERON),
        "wells": wells_content,
    }

    return {"data": {"type": "plates", "attributes": body}}
