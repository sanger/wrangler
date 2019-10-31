import pytest
from app import app

TUBE_RACK_URL = '/tube_rack'
VALID_FILE = 'test_valid_file'
INVALID_FILE = 'test_invalid_file'

@pytest.fixture
def client():
    app.testing = True
    app.config['TUBE_RACK_DIR'] = './tests/'

    with app.test_client() as client:
        yield client


def test_file_not_provided(client):
    assert client.get(TUBE_RACK_URL).status_code == 404


def test_valid_file(client):
    output = {
        "rack_barcode": VALID_FILE,
        "layout": [{"a1": "test_barcode"}, {"b1": "test_barcode2"}]
    }
    response = client.get(f'{TUBE_RACK_URL}/{VALID_FILE}')
    assert response.status_code == 200
    assert response.get_json() == output


def test_file_not_found(client):
    assert client.get(f'{TUBE_RACK_URL}/574').status_code == 404


def test_invalid_file(client):
    response = client.get(f'{TUBE_RACK_URL}/{INVALID_FILE}')
    print(response.data)
    assert response.status_code == 500
