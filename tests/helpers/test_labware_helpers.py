from pytest import raises

from wrangler.exceptions import BarcodeNotFoundError
from wrangler.helpers.labware_helpers import wrangle_labware


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
