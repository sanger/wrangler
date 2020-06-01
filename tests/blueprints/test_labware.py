from http import HTTPStatus
from urllib.parse import urlencode

import responses
from flask import current_app

WRANGLE_URL = "/wrangle"
VALID_BARCODE = "DN123"
INVALID_BARCODE = "DN_invalid"
LESS_TUBES_BARCODE = "DN_lesstubes"
DIFF_TUBES_BARCODE = "DN_difftubes"
SIZE48_BARCODE = "DN_48_valid"


def test_fail_if_num_tubes_from_layout_and_mlwh_do_not_match(app, client, mocked_responses):
    """This tests what happens when there are less tubes in the MLWH. The CSV file needs the 48/96
    rows for it to pass validation and to check for TubesCountError.

    Deleted first 3 rows from DN_48_less_tubes.sql.
    """
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]}'
        )
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.OK)

        response = client.post(f"{WRANGLE_URL}/DN_48_less_tubes")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "TubesCountError" in response.get_json()["error"]


def test_fail_if_any_tube_barcode_different_between_layout_and_mlwh(app, client, mocked_responses):
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]}'
        )
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.OK)
        response = client.post(f"{WRANGLE_URL}/DN_48_barcode_mismatch")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "BarcodesMismatchError" in response.get_json()["error"]


def test_valid_barcode_wrangle(app, client, mocked_responses):
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_ENDPOINT"]}'
        )

        purpose_url = f"http://{current_app.config['SS_HOST']}/api/v2/purposes?{urlencode({'filter[name]': 'TR Stock 96'})}"
        study_url = f"http://{current_app.config['SS_HOST']}/api/v2/studies?{urlencode({'filter[name]': 'heron'})}"

        # Entity Lookups
        mocked_responses.add(
            responses.GET, purpose_url, json={"data": [{"attributes": {"uuid": "1111"}}]}
        )
        mocked_responses.add(
            responses.GET, study_url, json={"data": [{"attributes": {"uuid": "2222"}}]}
        )

        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED)
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED)

        response = client.post(f"{WRANGLE_URL}/DN_48_valid")

        assert response.status_code == HTTPStatus.CREATED
        assert response.get_json() == {}

        response = client.post(f"{WRANGLE_URL}/DN_96_valid")

        assert response.status_code == HTTPStatus.CREATED
        assert response.get_json() == {}


def test_invalid_barcode_wrangle(client):
    response = client.post(f"{WRANGLE_URL}/{INVALID_BARCODE}")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_indeterminable_wrangle(app, client):
    """Test when some of the tube barcodes are empty and some are populated."""
    with app.app_context():
        response = client.post(f"{WRANGLE_URL}/DN_48_indeterminable")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "IndeterminableLabwareError" in response.get_json()["error"]


