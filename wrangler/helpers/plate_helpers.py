import logging
from typing import Dict, List, Union

from flask import current_app as app

from wrangler.helpers.general_helpers import send_request_to_sequencescape
from wrangler.helpers.sample_helpers import sample_contents_for

logger = logging.getLogger(__name__)


def create_plate_body(
    plate_barcode: str, mlwh_results: List[Dict[str, str]], purpose_uuid: str, study_uuid: str,
) -> Dict[str, Union[str, Dict]]:
    wells_content = {}
    for sample in mlwh_results:
        wells_content[sample["position"]] = {
            "content": sample_contents_for(sample["supplier_sample_id"])
        }

    body = {
        "barcode": plate_barcode,
        "wells": wells_content,
        "purpose_uuid": purpose_uuid,
        "study_uuid": study_uuid,
    }

    return {"data": {"type": "plates", "attributes": body}}


def create_plate(plate_body: Dict[str, Union[str, Dict]]):
    return send_request_to_sequencescape(app.config["SS_TUBE_RACK_ENDPOINT"], plate_body)
