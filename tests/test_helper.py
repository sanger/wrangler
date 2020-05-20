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
    control_for,
    control_type_for,
    add_control_sample_if_present,
    PURPOSE_TR_STOCK_48,
)

import wrangler.helper

from unittest import mock


def test_send_request_to_sequencescape(app, client, mocked_responses):
    with app.app_context():
        ss_url = f'{current_app.config["SS_PROTOCOL"]}://{current_app.config["SS_HOST"]}/test'

        mocked_responses.add(
            responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED,
        )
        response = send_request_to_sequencescape("/test", {})
        assert response == HTTPStatus.CREATED


def test_wrangle_tubes(app, client):
    output = {
        "data": {
            "attributes": {
                "tube_rack": {
                    "barcode": "DN123",
                    "purpose_uuid": "TESTING_PURPOSE_UUID",
                    "study_uuid": "TESTING_STUDY_UUID",
                    "tubes": {
                        "A01": {"barcode": "TB123", "content": {"supplier_name": "PHEC-nnnnnnn2"}},
                        "A02": {"barcode": "TB124", "content": {"supplier_name": "PHEC-nnnnnnn3"}},
                        "A03": {"barcode": "TB125", "content": {"supplier_name": "PHEC-nnnnnnn4"}},
                        "B01": {"barcode": "TB126", "content": {"supplier_name": "PHEC-nnnnnnn5"}},
                        "B02": {"barcode": "TB127", "content": {"supplier_name": "PHEC-nnnnnnn6"}},
                        "B03": {"barcode": "TB128", "content": {"supplier_name": "PHEC-nnnnnnn7"}},
                    },
                }
            }
        }
    }
    with app.app_context():
        with mock.patch.object(
            wrangler.helper, "get_study_uuid", return_value="TESTING_STUDY_UUID"
        ):
            with mock.patch.object(
                wrangler.helper, "get_purpose_uuid", return_value="TESTING_PURPOSE_UUID"
            ):

                tube_request_body = wrangle_tubes("DN123")

                assert tube_request_body == output

                with raises(BarcodeNotFoundError):
                    wrangle_tubes("")


def test_wrangle_control_tubes(app, client):
    output = {
        "data": {
            "attributes": {
                "tube_rack": {
                    "barcode": "DN_control",
                    "purpose_uuid": "TESTING_PURPOSE_UUID",
                    "study_uuid": "TESTING_STUDY_UUID",
                    "tubes": {
                        "A01": {"barcode": "TB133", "content": {"supplier_name": "PHEC-nnnnnnn60"}},
                        "A02": {
                            "barcode": "TB134",
                            "content": {
                                "supplier_name": "Positive control",
                                "control": True,
                                "control_type": "Positive",
                            },
                        },
                        "A03": {
                            "barcode": "TB135",
                            "content": {
                                "supplier_name": "Negative control",
                                "control": True,
                                "control_type": "Negative",
                            },
                        },
                        "A04": {
                            "barcode": "TB136",
                            "content": {
                                "supplier_name": "Control",
                                "control": True,
                                "control_type": None,
                            },
                        },
                    },
                }
            }
        }
    }
    with app.app_context():
        with mock.patch.object(
            wrangler.helper, "get_study_uuid", return_value="TESTING_STUDY_UUID"
        ):
            with mock.patch.object(
                wrangler.helper, "get_purpose_uuid", return_value="TESTING_PURPOSE_UUID"
            ):
                tube_request_body = wrangle_tubes("DN_control")

                assert tube_request_body == output

                with raises(BarcodeNotFoundError):
                    wrangle_tubes("")


def test_wrangle_tubes_size_48(app, client):
    with app.app_context():
        with mock.patch.object(
            wrangler.helper, "get_study_uuid", return_value="TESTING_STUDY_UUID"
        ):
            with mock.patch.object(
                wrangler.helper, "get_purpose_uuid", return_value="TESTING_PURPOSE_UUID"
            ) as mocked:

                tube_request_body = wrangle_tubes("DN_size48")

                assert (
                    tube_request_body["data"]["attributes"]["tube_rack"]["purpose_uuid"]
                    == "TESTING_PURPOSE_UUID"
                )

                mocked.assert_called_once_with(PURPOSE_TR_STOCK_48)

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


def test_control_for_normal_sample():
    supplier_sample_id = "A sample"
    assert control_for(supplier_sample_id) == False
    assert control_type_for(supplier_sample_id) == None


def test_control_for_positive_control():
    supplier_sample_id = "A sample with positive control and other stuff"
    assert control_for(supplier_sample_id) == True
    assert control_type_for(supplier_sample_id) == "Positive"


def test_control_for_negative_control():
    supplier_sample_id = "a negative control sample"
    assert control_for(supplier_sample_id) == True
    assert control_type_for(supplier_sample_id) == "Negative"


def test_control_for_control():
    supplier_sample_id = "A sample it has a control in it and other stuff"
    assert control_for(supplier_sample_id) == True
    assert control_type_for(supplier_sample_id) == None


def test_set_add_control_sample_if_present():
    record = {"content": {"supplier_name": "is a positive control"}}
    add_control_sample_if_present(record)
    assert record["content"]["control"] == True
    assert record["content"]["control_type"] == "Positive"


def test_not_set_control_sample_if_not_present():
    record = {"content": {"supplier_name": "is a very positive sample"}}
    add_control_sample_if_present(record)
    assert not "control" in record["content"]
