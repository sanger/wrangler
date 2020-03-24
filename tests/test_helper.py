from http import HTTPStatus

import responses
from flask import current_app
from pytest import raises

from wrangler.exceptions import (
    BarcodeNotFoundError,
    BarcodesMismatchError,
    TubesCountError,
)
from wrangler.helper import send_request_to_sequencescape, validate_tubes, wrangle_tubes


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

        with raises(BarcodeNotFoundError):
            wrangle_tubes("")


def test_validate_tubes_different_barcodes():
    with raises(BarcodesMismatchError):
        assert validate_tubes({"T1": 1, "T2": 2}, {"T2": 1, "T3": 1})


def test_validate_tubes_more_in_layout():
    with raises(TubesCountError):
        assert validate_tubes({"T1": 1, "T2": 2}, {"T2": 1})


def test_validate_tubes_less_in_layout():
    with raises(TubesCountError):
        assert validate_tubes({"T1": 1}, {"T1": 1, "T2": 1})


def test_validate_tubes_duplication():
    with raises(TubesCountError):
        assert validate_tubes({"T1": 1, "T1": 1}, {"T1": 1, "T2": 1})


def test_validate_tubes_different_order():
    assert validate_tubes({"T1": 1, "T2": 1}, {"T2": 1, "T1": 1}) is True
