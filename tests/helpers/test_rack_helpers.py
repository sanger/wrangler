from pytest import raises

from wrangler.exceptions import BarcodesMismatchError, TubesCountError
from wrangler.helpers.rack_helpers import create_tube_rack_body, parse_tube_rack_csv, validate_tubes


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


def test_parse_tube_rack_csv(app_db_less):
    with app_db_less.app_context():
        assert parse_tube_rack_csv("DN123") == {
            "rack_barcode": "DN123",
            "layout": {
                "TB123": "A01",
                "TB124": "A02",
                "TB125": "A03",
                "TB126": "B01",
                "TB127": "B02",
                "TB128": "B03",
            },
        }

        with raises(FileNotFoundError):
            assert parse_tube_rack_csv("blah") is None


def test_parse_tube_rack_csv_ignores_no_read(app_db_less, client, tmpdir):
    with app_db_less.app_context():
        sub = tmpdir.mkdir("sub")
        myfile = sub.join("DN456.csv")
        app_db_less.config["TUBE_RACK_DIR"] = sub
        content = "\n".join(["A01, F001", "B01, NO READ", "C01, F002"])

        myfile.write(content)

        expected_message = {
            "rack_barcode": "DN456",
            "layout": {"F001": "A01", "F002": "C01"},
        }
        assert parse_tube_rack_csv("DN456") == expected_message


def test_create_48_tube_rack_body(app_db_less, mocked_ss_calls_for_48_rack):
    with app_db_less.app_context():
        tubes = {
            "A01": { "barcode": "TB123", "contents": { "name": "xyz123", "supplier_sample_id": "xyz123"} },
            "A02": { "barcode": "TB456", "contents": { "name": "xyz456", "supplier_sample_id": "xyz456"} }
        }
        size = 48
        tube_rack_barcode = "DN123"
        tube_rack_response = {
            "tube_rack": {
                "study_uuid": "study_heron_uuid",
                "purpose_uuid": "purpose_rack_48_uuid",
                "barcode": tube_rack_barcode, 
                "tubes": tubes
            }
        }
        body = {"data": {"attributes": tube_rack_response}}

        assert create_tube_rack_body(size, tube_rack_barcode, tubes) == body

def test_create_96_tube_rack_body(app_db_less, mocked_ss_calls_for_96_rack):
    with app_db_less.app_context():
        tubes = {
            "A01": { "barcode": "TB123", "contents": { "name": "xyz123", "supplier_sample_id": "xyz123"} },
            "A02": { "barcode": "TB456", "contents": { "name": "xyz456", "supplier_sample_id": "xyz456"} }
        }
        size = 96
        tube_rack_barcode = "DN123"
        tube_rack_response = {
            "tube_rack": {
                "study_uuid": "study_heron_uuid",
                "purpose_uuid": "purpose_rack_96_uuid",
                "barcode": tube_rack_barcode, 
                "tubes": tubes
            }
        }
        body = {"data": {"attributes": tube_rack_response}}

        assert create_tube_rack_body(size, tube_rack_barcode, tubes) == body