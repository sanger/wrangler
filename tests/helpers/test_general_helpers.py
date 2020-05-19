from http import HTTPStatus

import responses
from flask import current_app
from pytest import raises

from wrangler.constants import PLATE, STATUS_VALIDATION_FAILED, TUBE_RACK
from wrangler.exceptions import BarcodeNotFoundError, IndeterminableLabwareError
from wrangler.helpers.general_helpers import (
    csv_file_exists,
    determine_labware_type,
    error_request_body,
    handle_error,
    send_request_to_sequencescape,
)


def test_send_request_to_sequencescape(app, client, mocked_responses):
    with app.app_context():
        ss_url = f'{current_app.config["SS_PROTOCOL"]}://{current_app.config["SS_HOST"]}/test'

        mocked_responses.add(
            responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED,
        )
        response = send_request_to_sequencescape("/test", {})
        assert response == HTTPStatus.CREATED


def test_wrangle_labware(app, client):
    output = {
        "data": {
            "attributes": {
                "tube_rack": {
                    "barcode": "DN123",
                    "size": 96,
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
        tube_request_body = wrangle_labware("DN123")

        assert tube_request_body == output

        with raises(BarcodeNotFoundError):
            wrangle_labware("")


def test_wrangle_labware_size_48(app, client):
    with app.app_context():
        tube_request_body = wrangle_labware("DN_size48")

        assert tube_request_body["data"]["attributes"]["tube_rack"]["size"] == 48

        with raises(BarcodeNotFoundError):
            wrangle_labware("")


def test_handle_error(app):
    barcode_error = BarcodeNotFoundError("blah")
    tube_rack_barcode = "DN123"
    with app.app_context():
        assert handle_error(barcode_error, tube_rack_barcode) == ({}, HTTPStatus.NO_CONTENT,)
        assert handle_error(Exception("blah"), tube_rack_barcode) == (
            {"error": "Exception"},
            HTTPStatus.OK,
        )


def test_error_request_body():
    tube_rack_barcode = "DN456"
    exception = Exception("blah")
    body = {
        "data": {
            "attributes": {
                "tube_rack_status": {
                    "tube_rack": {
                        "barcode": tube_rack_barcode,
                        "status": STATUS_VALIDATION_FAILED,
                        "messages": [str(exception)],
                    }
                }
            }
        }
    }
    assert error_request_body(exception, tube_rack_barcode) == body


def test_csv_file_exists(app):
    with app.app_context():
        assert csv_file_exists("DN123.csv") is True
        assert csv_file_exists("does not exist") is False


def test_determine_labware_type(app):
    with app.app_context():
        assert (
            determine_labware_type([{"tube_barcode": "123"}, {"tube_barcode": "456"}]) == TUBE_RACK
        )

        assert determine_labware_type([{"tube_barcode": None}, {"tube_barcode": None}]) == PLATE

        with raises(IndeterminableLabwareError):
            determine_labware_type([{"tube_barcode": None}, {"tube_barcode": "123"}])
