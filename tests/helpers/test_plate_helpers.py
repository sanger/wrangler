from http import HTTPStatus

import responses
from flask import current_app

from wrangler.constants import PLATE_PURPOSE_ENTITY, PLATE_PURPOSE_STOCK, STUDY_ENTITY, STUDY_HERON
from wrangler.helpers.plate_helpers import create_plate_body


def test_create_plate_body(app_db_less, mocked_responses):
    samples = [
        {"coordinate": "A01", "supplie_sample_id": "xyz123"},
        {"coordinate": "A02", "supplie_sample_id": "xyz456"},
    ]
    wells_content = {
        "A01": {"supplier_name": "xyz123"},
        "A02": {"supplier_name": "xyz456"},
    }
    plate_barcode = "DN123"
    plate_purpose_uuid = "54321"
    study_uuid = "12345"
    body = {
        "barcode": plate_barcode,
        "plate_purpose_uuid": plate_purpose_uuid,
        "study_uuid": "12345",
        "wells_content": wells_content,
    }

    with app_db_less.app_context():
        ss_url = f'http://{current_app.config["SS_HOST"]}'
        studies_endpoint = f"/api/v2/{STUDY_ENTITY}?filter[name]={STUDY_HERON}"
        plate_purpose_endpoint = (
            f"/api/v2/{PLATE_PURPOSE_ENTITY}?filter[name]={PLATE_PURPOSE_STOCK}"
        )

        mocked_responses.add(
            responses.GET,
            f"{ss_url}{studies_endpoint}",
            body=f'{{"data":{{"attributes": {{"uuid":"{study_uuid}"}}}}}}',
            status=HTTPStatus.OK,
        )
        mocked_responses.add(
            responses.GET,
            f"{ss_url}{plate_purpose_endpoint}",
            body=f'{{"data":{{"attributes": {{"uuid":"{plate_purpose_uuid}"}}}}}}',
            status=HTTPStatus.OK,
        )
        assert create_plate_body(plate_barcode, samples) == {
            "data": {"type": "plates", "attributes": body}
        }
