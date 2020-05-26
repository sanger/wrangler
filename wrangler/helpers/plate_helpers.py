import logging
from typing import Dict, List, Union

from flask import current_app as app

from wrangler.helpers.general_helpers import send_request_to_sequencescape

logger = logging.getLogger(__name__)


def create_plate_body(
    plate_barcode: str,
    mlwh_results: List[Dict[str, str]],
    plate_purpose_uuid: str = None,
    study_uuid: str = None,
) -> Dict[str, Union[str, Dict]]:
    wells_content = {}
    for sample in mlwh_results:
        well = {
            "supplier_name": sample["supplier_sample_id"],
        }
        wells_content[sample["position"]] = well

    body = {
        "barcode": plate_barcode,
        "wells_content": wells_content,
    }

    if plate_purpose_uuid is not None:
        body["plate_purpose_uuid"] = plate_purpose_uuid

    if study_uuid is not None:
        body["study_uuid"] = study_uuid

    return {"data": {"type": "plates", "attributes": body}}


def create_plate(plate_body: Dict[str, Union[str, Dict]]):
    return send_request_to_sequencescape(app.config["SS_TUBE_RACK_ENDPOINT"], plate_body)
