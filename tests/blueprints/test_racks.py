from http import HTTPStatus

TUBE_RACK_URL = "/tube_rack"
VALID_BARCODE = "DN123"
INVALID_BARCODE = "DN_invalid"
LESS_TUBES_BARCODE = "DN_lesstubes"
DIFF_TUBES_BARCODE = "DN_difftubes"
SIZE48_BARCODE = "DN_size48"


def test_barcode_not_provided(client):
    assert client.get(TUBE_RACK_URL).status_code == HTTPStatus.NOT_FOUND


def test_barcode_not_found(client):
    response = client.get(f"{TUBE_RACK_URL}/blah")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_invalid_tube_rack_file(client):
    """This tests that despite the barcode being valid, the tube rack file might be invalid.
    """
    response = client.get(f"{TUBE_RACK_URL}/{INVALID_BARCODE}")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_valid_tube_rack_file(client):
    output = {
        "rack_barcode": VALID_BARCODE,
        "layout": {
            "TB123": "A01",
            "TB124": "A02",
            "TB125": "A03",
            "TB126": "B01",
            "TB127": "B02",
            "TB128": "B03",
        },
    }
    response = client.get(f"{TUBE_RACK_URL}/{VALID_BARCODE}")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == output
