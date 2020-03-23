from http import HTTPStatus

from wrangler.exceptions import *

from wrangler.helper import validate_tubes

from pytest import raises

TUBE_RACK_URL = "/tube_rack"
WRANGLE_URL = "/wrangle"
VALID_BARCODE = "DN123"
INVALID_BARCODE = "DN_invalid"
LESS_TUBES_BARCODE = "DN_lesstubes"
DIFF_TUBES_BARCODE = "DN_difftubes"

def test_barcode_not_provided(client):
    assert client.get(TUBE_RACK_URL).status_code == HTTPStatus.NOT_FOUND


def test_fail_if_num_tubes_from_layout_and_mlwh_dont_match(app, client):
    response = client.get(f"{WRANGLE_URL}/{LESS_TUBES_BARCODE}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json['error'] == DifferentNumTubesLayoutAndDatabase.message

def test_fail_if_any_tube_barcode_different_between_layout_and_mlwh(app, client):
    response = client.get(f"{WRANGLE_URL}/{DIFF_TUBES_BARCODE}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json['error'] == DifferentBarcodesLayoutAndDatabase.message

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
        "error": TubeRackBarcodeNotFoundInDatabase.message
    }

def test_validate_tubes_different_barcodes():
    with raises(DifferentBarcodesLayoutAndDatabase):
        assert validate_tubes({'T1': 1, 'T2':2},{'T2': 1, 'T3': 1})

def test_validate_tubes_more_in_layout():
    with raises(DifferentNumTubesLayoutAndDatabase):
        assert validate_tubes({'T1': 1, 'T2':2},{'T2': 1})

def test_validate_tubes_less_in_layout():
    with raises(DifferentNumTubesLayoutAndDatabase):
        assert validate_tubes({'T1': 1},{'T1': 1,'T2': 1})

def test_validate_tubes_duplication():
    with raises(DifferentNumTubesLayoutAndDatabase):
        assert validate_tubes({'T1': 1, 'T1':1},{'T1': 1,'T2': 1})

def test_validate_tubes_different_order():
    assert validate_tubes({'T1': 1, 'T2':1},{'T2': 1,'T1': 1}) == True
