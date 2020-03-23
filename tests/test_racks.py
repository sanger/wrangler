from http import HTTPStatus


TUBE_RACK_URL = "/tube_rack"
WRANGLE_URL = "/wrangle"
VALID_BARCODE = "DN123"
INVALID_BARCODE = "DN_invalid"
MISMATCHED_BARCODE = "DN_mismatch"


def test_barcode_not_provided(client):
    assert client.get(TUBE_RACK_URL).status_code == HTTPStatus.NOT_FOUND


def test_fail_if_tubes_from_layout_and_mlwh_dont_match(app, client):
    assert client.get(f"{TUBE_RACK_URL}/{MISMATCHED_BARCODE}") == HTTPStatus.INTERNAL_SERVER_ERROR


def test_valid_file(client):
    output = {
        "rack_barcode": VALID_BARCODE,
        "layout": {
            "TB123": "A01",
            "TB124": "A02",
            "TB125": "A03",
            "TB126": "B01",
            "TB127": "B02",
            "TB128": "B03"
        },
    }
    response = client.get(f"{TUBE_RACK_URL}/{VALID_BARCODE}")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == output


def test_barcode_not_found(client):
    assert client.get(f"{TUBE_RACK_URL}/blah").status_code == HTTPStatus.NOT_FOUND


def test_invalid_barcode(client):
    response = client.get(f"{TUBE_RACK_URL}/{INVALID_BARCODE}")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_valid_barcode_wrangle(client):
    response = client.get(f"{WRANGLE_URL}/{VALID_BARCODE}")
    assert response.status_code == HTTPStatus.OK
    assert response.data == b"POST request successfully sent to Sequencescape"


def test_invalid_barcode_wrangle(client):
    response = client.get(f"{WRANGLE_URL}/{INVALID_BARCODE}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {
        "error": "Server error: Tube rack barcode not found in the MLWH"
    }
