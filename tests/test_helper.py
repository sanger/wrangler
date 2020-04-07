from http import HTTPStatus

import responses
from flask import current_app
from pytest import raises

from wrangler.exceptions import BarcodeNotFoundError, BarcodesMismatchError, TubesCountError
from wrangler.helper import (
    STATUS_VALIDATION_FAILED,
    error_request_body,
    handle_error,
    parse_tube_rack_csv,
    send_request_to_sequencescape,
    validate_tubes,
    wrangle_tubes,
)


def test_send_request_to_sequencescape(app, client, mocked_responses):
    with app.app_context():
        ss_url = f'{current_app.config["SS_PROTOCOL"]}://{current_app.config["SS_HOST"]}/test'

        mocked_responses.add(
            responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED,
        )
        response = send_request_to_sequencescape("test", {})
        assert response == HTTPStatus.CREATED


def test_wrangle_tubes(app, client):
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
        tube_request_body = wrangle_tubes("DN123")

        assert tube_request_body == output

        with raises(BarcodeNotFoundError):
            wrangle_tubes("")


def test_wrangle_tubes_size_48(app, client):
    with app.app_context():
        tube_request_body = wrangle_tubes("DN_size48")

        assert tube_request_body["data"]["attributes"]["tube_rack"]["size"] == 48

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


def test_parse_tube_rack_csv_ignores_no_read(app, client, tmpdir):
    with app.app_context():
        sub = tmpdir.mkdir("sub")
        myfile = sub.join("DN456.csv")
        app.config["TUBE_RACK_DIR"] = sub
        content = "\n".join(["A01, F001", "B01, NO READ", "C01, F002"])

        myfile.write(content)

        expected_message = {
            "rack_barcode": "DN456",
            "layout": {"F001": "A01", "F002": "C01"},
        }
        assert parse_tube_rack_csv("DN456") == expected_message


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
