from http import HTTPStatus

import responses
from flask import current_app
from pytest import raises

from wrangler.constants import (
    STATUS_VALIDATION_FAILED,
    EXTRACT_TR_PURPOSE_96,
    LYSATE_TR_PURPOSE,
    EXTRACT_PLATE_PURPOSE,
    LYSATE_PLATE_PURPOSE
)
from wrangler.exceptions import (
    BarcodeNotFoundError,
    IndeterminableLabwareError,
    IndeterminableSampleTypeError,
    IndeterminablePurposeError
)
from wrangler.helpers.general_helpers import (
    csv_file_exists,
    determine_labware_type,
    LabwareType,
    determine_sample_type,
    SampleType,
    determine_purpose_name,
    error_request_body,
    get_entity_uuid,
    handle_error,
    send_request_to_sequencescape,
)


def test_send_request_to_sequencescape(app_db_less, mocked_responses):
    with app_db_less.app_context():
        ss_url = f'http://{current_app.config["SS_HOST"]}/test'

        mocked_responses.add(
            responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED,
        )
        mocked_responses.add(responses.POST, ss_url, body=Exception("blah"))

        assert send_request_to_sequencescape("/test", {}) == ({}, HTTPStatus.CREATED)

        with raises(Exception):
            send_request_to_sequencescape("/test", {})


def test_handle_error(app_db_less, mocked_responses):
    barcode_error = BarcodeNotFoundError("blah")
    labware_barcode = "DN123"
    with app_db_less.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]}'
        )

        mocked_responses.add(
            responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED,
        )
        mocked_responses.add(
            responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED,
        )

        assert handle_error(
            barcode_error, labware_barcode, current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]
        ) == ({}, HTTPStatus.NO_CONTENT)

        assert handle_error(
            Exception("blah"), labware_barcode, current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]
        ) == ({"error": "Exception: blah"}, HTTPStatus.INTERNAL_SERVER_ERROR)


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


def test_csv_file_exists(app_db_less):
    with app_db_less.app_context():
        assert csv_file_exists("DN_48_valid.csv") is True
        assert csv_file_exists("does not exist") is False


def test_determine_labware_type(app_db_less):
    with app_db_less.app_context():
        assert (
            determine_labware_type("blah", [{"tube_barcode": "123"}, {"tube_barcode": "456"}])
            == LabwareType.TUBE_RACK
        )

        assert (
            determine_labware_type("blah", [{"tube_barcode": None}, {"tube_barcode": None}])
            == LabwareType.PLATE
        )

        with raises(IndeterminableLabwareError):
            determine_labware_type("blah", [{"tube_barcode": None}, {"tube_barcode": "123"}])

def test_determine_sample_type(app_db_less):
    with app_db_less.app_context():
        assert (
            determine_sample_type("blah", [{"sample_state": "Extract"}, {"sample_state": "Extract"}])
            == SampleType.EXTRACT
        )

        assert (
            determine_sample_type("blah", [{"sample_state": "Lysate"}, {"sample_state": "Lysate"}])
            == SampleType.LYSATE
        )

        with raises(IndeterminableSampleTypeError):
            determine_sample_type("blah", [{"sample_state": "stuff"}, {"sample_state": "stuff"}])

def test_determine_purpose_name(app_db_less):
    with app_db_less.app_context():
        assert (
            determine_purpose_name("blah", LabwareType.TUBE_RACK, SampleType.EXTRACT)
            == EXTRACT_TR_PURPOSE_96
        )

        assert (
            determine_purpose_name("blah", LabwareType.TUBE_RACK, SampleType.LYSATE)
            == LYSATE_TR_PURPOSE
        )

        assert (
            determine_purpose_name("blah", LabwareType.PLATE, SampleType.EXTRACT)
            == EXTRACT_PLATE_PURPOSE
        )

        assert (
            determine_purpose_name("blah", LabwareType.PLATE, SampleType.LYSATE)
            == LYSATE_PLATE_PURPOSE
        )

        with raises(IndeterminablePurposeError):
            determine_purpose_name("blah", "stuff", "thing")

def test_get_entity_uuid(app_db_less, mocked_responses):
    with app_db_less.app_context():
        entity = "dog"
        entity_name = "apollo"
        uuid = "12345"

        ss_url = (
            f"http://{current_app.config['SS_HOST']}/api/v2/{entity}?filter[name]={entity_name}"
        )

        mocked_responses.add(
            responses.GET,
            ss_url,
            body=f'{{"data": [{{"attributes": {{"uuid": "{uuid}"}}}}]}}',
            status=HTTPStatus.OK,
        )

        assert get_entity_uuid(entity, entity_name) == uuid


def test_get_entity_uuid_with_ampersand(app_db_less, mocked_responses):
    with app_db_less.app_context():
        entity = "studies"
        entity_name = "Heron Project R & D"
        uuid = "12345"

        # What the URL should look like after being encoded
        ss_url = f"http://{current_app.config['SS_HOST']}/api/v2/studies?filter%5Bname%5D=Heron+Project+R+%26+D"

        mocked_responses.add(
            responses.GET,
            ss_url,
            body=f'{{"data": [{{"attributes": {{"uuid": "{uuid}"}}}}]}}',
            status=HTTPStatus.OK,
        )

        assert get_entity_uuid(entity, entity_name) == uuid
