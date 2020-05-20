from http import HTTPStatus

import responses
from flask import current_app

WRANGLE_URL = "/wrangle"
VALID_BARCODE = "DN123"
INVALID_BARCODE = "DN_invalid"
LESS_TUBES_BARCODE = "DN_lesstubes"
DIFF_TUBES_BARCODE = "DN_difftubes"
SIZE48_BARCODE = "DN_size48"


def test_fail_if_num_tubes_from_layout_and_mlwh_do_not_match(app, client, mocked_responses):
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]}'
        )
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.OK)
        response = client.post(f"{WRANGLE_URL}/{LESS_TUBES_BARCODE}")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "TubesCountError" in response.get_json()["error"]


def test_fail_if_any_tube_barcode_different_between_layout_and_mlwh(app, client, mocked_responses):
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_STATUS_ENDPOINT"]}'
        )
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.OK)
        response = client.post(f"{WRANGLE_URL}/{DIFF_TUBES_BARCODE}")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "BarcodesMismatchError" in response.get_json()["error"]


def test_valid_barcode_wrangle(app, client, mocked_responses):
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_ENDPOINT"]}'
        )
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED)
        response = client.post(f"{WRANGLE_URL}/{VALID_BARCODE}")
        assert response.status_code == HTTPStatus.CREATED
        assert response.get_json() == {}


def test_invalid_barcode_wrangle(client):
    response = client.post(f"{WRANGLE_URL}/{INVALID_BARCODE}")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_size48_wrangle(app, client, mocked_responses):
    with app.app_context():
        ss_url = (
            f'http://{current_app.config["SS_HOST"]}'
            f'{current_app.config["SS_TUBE_RACK_ENDPOINT"]}'
        )
        mocked_responses.add(responses.POST, ss_url, body="{}", status=HTTPStatus.CREATED)
        response = client.post(f"{WRANGLE_URL}/{SIZE48_BARCODE}")
        assert response.status_code == HTTPStatus.CREATED
        assert response.get_json() == {}
