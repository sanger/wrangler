from wrangler.helpers.plate_helpers import create_plate_body


def test_create_plate_body():
    samples = [
        {"position": "A01", "supplier_sample_id": "xyz123"},
        {"position": "A02", "supplier_sample_id": "xyz456"},
    ]
    wells_content = {
        "A01": {"content": {"supplier_name": "xyz123"}},
        "A02": {"content": {"supplier_name": "xyz456"}},
    }
    plate_barcode = "DN123"
    plate_purpose_uuid = "54321"
    study_uuid = "12345"
    body = {
        "barcode": plate_barcode,
        "purpose_uuid": plate_purpose_uuid,
        "study_uuid": "12345",
        "wells": wells_content,
    }

    assert create_plate_body(
        plate_barcode, samples, plate_purpose_uuid=plate_purpose_uuid, study_uuid=study_uuid
    ) == {"data": {"type": "plates", "attributes": body}}
