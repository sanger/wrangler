from pytest import raises

from wrangler.constants import DEFAULT_TUBE_RACK_SIZE
from wrangler.exceptions import BarcodesMismatchError, TubesCountError
from wrangler.helpers.rack_helpers import create_tube_rack_body, parse_tube_rack_csv, validate_tubes


def test_validate_tubes_different_barcodes():
    with raises(BarcodesMismatchError):
        assert validate_tubes("blah", {"T1": 1, "T2": 2}, {"T2": 1, "T3": 1})


def test_validate_tubes_more_in_layout():
    with raises(TubesCountError):
        assert validate_tubes("blah", {"T1": 1, "T2": 2}, {"T2": 1})


def test_validate_tubes_less_in_layout():
    with raises(TubesCountError):
        assert validate_tubes("blah", {"T1": 1}, {"T1": 1, "T2": 1})


def test_validate_tubes_duplication():
    with raises(TubesCountError):
        assert validate_tubes("blah", {"T1": 1, "T1": 1}, {"T1": 1, "T2": 1})


def test_validate_tubes_different_order():
    assert validate_tubes("blah", {"T1": 1, "T2": 1}, {"T2": 1, "T1": 1}) is True


def test_parse_tube_rack_csv(app_db_less):
    with app_db_less.app_context():
        rack_size, tube_dict = parse_tube_rack_csv("DN_48_valid")
        assert rack_size == 48
        assert tube_dict == {
            "rack_barcode": "DN_48_valid",
            "layout": {
                "FR05653780": "A1",
                "FR05653808": "A2",
                "FR05653791": "A3",
                "FR05653668": "A4",
                "FR05653832": "A5",
                "FR05653743": "A6",
                "FR05653698": "A7",
                "FR05653716": "A8",
                "FR05653773": "B1",
                "FR05653774": "B2",
                "FR05653756": "B3",
                "FR05653730": "B4",
                "FR05653765": "B5",
                "FR05653687": "B6",
                "FR05653753": "B7",
                "FR05653747": "B8",
                "FR05653671": "C1",
                "FR05653623": "C2",
                "FR05653758": "C3",
                "FR05653845": "C4",
                "FR05653704": "C5",
                "FR05653642": "C6",
                "FR05653770": "C7",
                "FR05653630": "C8",
                "FR05653796": "D1",
                "FR05653795": "D2",
                "FR05653769": "D3",
                "FR05653777": "D4",
                "FR05653734": "D5",
                "FR05653703": "D6",
                "FR05653783": "D7",
                "FR05653748": "D8",
                "FR05653735": "E1",
                "FR05653824": "E2",
                "FR05653725": "E3",
                "FR05653789": "E4",
                "FR05653797": "E5",
                "FR05653624": "E6",
                "FR05653812": "E7",
                "FR05653784": "E8",
                "FR05653628": "F1",
                "FR05653658": "F2",
                "FR05653733": "F3",
                "FR05653678": "F4",
                "FR05653699": "F5",
                "FR05653785": "F6",
                "FR05653736": "F7",
                "FR05653732": "F8",
            },
        }

        with raises(FileNotFoundError):
            parse_tube_rack_csv("blah")


def test_parse_tube_rack_csv_ignores_no_read(app_db_less, client, tmpdir):
    with app_db_less.app_context():

        expected_output = {
            "rack_barcode": "DN_48_no_read",
            "layout": {"FR05653780": "A1", "FR05653808": "A2", "FR05653801": "F8"},
        }
        rack_size, tube_dict = parse_tube_rack_csv("DN_48_no_read")
        assert rack_size == 48
        assert tube_dict == expected_output


def test_create_tube_rack_body_with_size():
    tubes = [
        {"coordinate": "A01", "barcode": "TB123", "supplier_sample_id": "xyz123"},
        {"coordinate": "A02", "barcode": "TB456", "supplier_sample_id": "xyz456"},
    ]
    size = 48
    tube_rack_barcode = "DN123"
    tube_rack_response = {"tube_rack": {"barcode": tube_rack_barcode, "size": size, "tubes": tubes}}
    body = {"data": {"attributes": tube_rack_response}}

    assert create_tube_rack_body(tube_rack_barcode, tubes, size) == body


def test_create_tube_rack_body_without_size():
    tubes = [
        {"coordinate": "A01", "barcode": "TB123", "supplier_sample_id": "xyz123"},
        {"coordinate": "A02", "barcode": "TB456", "supplier_sample_id": "xyz456"},
    ]
    tube_rack_barcode = "DN123"
    tube_rack_response = {
        "tube_rack": {"barcode": tube_rack_barcode, "size": DEFAULT_TUBE_RACK_SIZE, "tubes": tubes}
    }
    body = {"data": {"attributes": tube_rack_response}}

    assert create_tube_rack_body(tube_rack_barcode, tubes) == body
