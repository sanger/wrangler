from http import HTTPStatus

import responses
from flask import current_app

from wrangler.helper import send_request_to_sequencescape, wrangle_tubes


def test_send_request_to_sequencescape(app, client, mocked_responses):
    with app.app_context():
        mocked_responses.add(
            responses.POST,
            current_app.config["SS_URL_HOST"],
            body="{}",
            status=HTTPStatus.CREATED,
        )
        response = send_request_to_sequencescape({})

        assert response == HTTPStatus.CREATED


def test_wrangle_tubes(app, client):
    output = {
        "data": {
            "attributes": {
                "tube_rack": {
                    "barcode": "DN123",
                    "tubes": [
                        {
                            "coordinate": "A01",
                            "barcode": "TB123",
                            "supplier_sample_id": "PHEC-nnnnnnn2",
                        },
                        {
                            "coordinate": "A02",
                            "barcode": "TB124",
                            "supplier_sample_id": "PHEC-nnnnnnn3",
                        },
                        {
                            "coordinate": "A03",
                            "barcode": "TB125",
                            "supplier_sample_id": "PHEC-nnnnnnn4",
                        },
                        {
                            "coordinate": "B01",
                            "barcode": "TB126",
                            "supplier_sample_id": "PHEC-nnnnnnn5",
                        },
                        {
                            "coordinate": "B02",
                            "barcode": "TB127",
                            "supplier_sample_id": "PHEC-nnnnnnn6",
                        },
                        {
                            "coordinate": "B03",
                            "barcode": "TB128",
                            "supplier_sample_id": "PHEC-nnnnnnn7",
                        },
                    ],
                }
            }
        }
    }
    with app.app_context():
        tube_request_body = wrangle_tubes("DN123")

        assert tube_request_body == output

        tube_request_body = wrangle_tubes("")
        assert tube_request_body is None
