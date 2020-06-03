from datetime import datetime
from unittest.mock import call

import wrangler.helpers.general_helpers as general_helpers
import wrangler.jobs.cgap_extraction as cgap_extraction
from wrangler.constants import (
    STUDY_ENTITY,
    PLATE_PURPOSE_ENTITY,
    HERON_PLATE_PURPOSE,
    HERON_TR_PURPOSE,
)
from wrangler.db import get_db


def test_get_unwrangled_labware(app):
    with app.app_context():
        results = cgap_extraction.get_unwrangled_labware("cgap_heron", "CGAP Extraction")
        assert len(results) == 7

        for row in results:
            assert row["destination"] == "CGAP Extraction"
            assert row["wrangled"] is None


def test_get_study_uuids(app, mocker):
    with app.app_context():
        mocker.patch.object(cgap_extraction, "get_entity_uuid")

        cgap_extraction.get_entity_uuid.side_effect = [
            "1000-0000-0000",
            "2000-0000-0000",
            "3000-0000-0000",
        ]

        result = cgap_extraction.get_study_uuids(["study1", "study2", "study3"])

        assert cgap_extraction.get_entity_uuid.call_count == 3
        assert call(STUDY_ENTITY, "study1") in cgap_extraction.get_entity_uuid.call_args_list
        assert call(STUDY_ENTITY, "study2") in cgap_extraction.get_entity_uuid.call_args_list
        assert call(STUDY_ENTITY, "study3") in cgap_extraction.get_entity_uuid.call_args_list

        assert result == {
            "study1": "1000-0000-0000",
            "study2": "2000-0000-0000",
            "study3": "3000-0000-0000",
        }


def test_get_plate_purpose_uuid(app, mocker):
    with app.app_context():
        mocker.patch.object(cgap_extraction, "get_entity_uuid")
        cgap_extraction.get_entity_uuid.return_value = "5555-5555-5555-5555"

        result = cgap_extraction.get_plate_purpose_uuid()

        assert (
            call(PLATE_PURPOSE_ENTITY, HERON_PLATE_PURPOSE)
            == cgap_extraction.get_entity_uuid.call_args
        )
        assert result == "5555-5555-5555-5555"


def test_get_tube_rack_purpose_uuids(app, mocker):
    with app.app_context():
        mocker.patch.object(cgap_extraction, "get_entity_uuid")
        cgap_extraction.get_entity_uuid.return_value = "8888-8888-8888-8888"

        result = cgap_extraction.get_tube_rack_purpose_uuid()

        assert (
            call(PLATE_PURPOSE_ENTITY, HERON_TR_PURPOSE)
            == cgap_extraction.get_entity_uuid.call_args
        )
        assert result == "8888-8888-8888-8888"


def test_create_labwares(app, mocker):
    with app.app_context():
        mocker.patch.object(cgap_extraction, "create_plate")
        mocker.patch.object(cgap_extraction, "create_plate_body")
        mocker.patch.object(cgap_extraction, "create_tube_rack")
        mocker.patch.object(cgap_extraction, "create_tube_rack_body")

        cgap_extraction.create_tube_rack.side_effect = [
            ["response1", 400],
        ]

        cgap_extraction.create_plate.side_effect = [
            ["response2", 201],
        ]

        rack_rows = [
            {
                "container_barcode": "RACK-1",
                "tube_barcode": "tb1",
                "study": "heron",
                "supplier_sample_id": "SSID1",
            },
            {
                "container_barcode": "RACK-1",
                "tube_barcode": "tb2",
                "study": "heron",
                "supplier_sample_id": "SSID2",
            },
            {
                "container_barcode": "RACK-1",
                "tube_barcode": "tb3",
                "study": "heron",
                "supplier_sample_id": "SSID3",
            },
            {
                "container_barcode": "RACK-1",
                "tube_barcode": "tb4",
                "study": "heron",
                "supplier_sample_id": "SSID4",
            },
        ]

        plate_rows = [
            {
                "container_barcode": "PLTE-1",
                "tube_barcode": None,
                "study": "heron r and d",
                "supplier_sample_id": "SSID5",
            },
            {
                "container_barcode": "PLTE-1",
                "tube_barcode": None,
                "study": "heron r and d",
                "supplier_sample_id": "SSID6",
            },
            {
                "container_barcode": "PLTE-1",
                "tube_barcode": None,
                "study": "heron r and d",
                "supplier_sample_id": "SSID7",
            },
        ]

        mlwh_rows = rack_rows + plate_rows

        study_uuids = {"heron": "3333", "heron r and d": "5555"}
        plate_purpose_uuids = {
            general_helpers.LabwareType.PLATE: "7777",
            general_helpers.LabwareType.TUBE_RACK: "9999",
        }

        result = cgap_extraction.create_labwares(
            mlwh_rows, study_uuids=study_uuids, plate_purpose_uuids=plate_purpose_uuids
        )

        ss_response = next(result)
        cgap_extraction.create_tube_rack_body.assert_called_with(
            "RACK-1", rack_rows, study_uuid="3333", purpose_uuid="9999"
        )
        assert cgap_extraction.create_tube_rack.call_count == 1
        assert ss_response.barcode == "RACK-1"
        assert ss_response.body == "response1"
        assert ss_response.successful is False

        ss_response = next(result)
        cgap_extraction.create_plate_body.assert_called_with(
            "PLTE-1", plate_rows, study_uuid="5555", purpose_uuid="7777"
        )
        assert cgap_extraction.create_plate.call_count == 1
        assert ss_response.barcode == "PLTE-1"
        assert ss_response.body == "response2"
        assert ss_response.successful is True


def test_update_wrangled(app):
    with app.app_context():
        results = cgap_extraction.update_wrangled_labware("cgap_heron", ["RACK-1"])
        assert results.rowcount == 3

        cursor = get_db()
        cursor.execute(
            f"SELECT wrangled FROM {app.config['MLWH_DB_TABLE']} WHERE container_barcode = 'RACK-1'"
        )

        for row in cursor:
            assert type(row["wrangled"]) is datetime


def test_run(app, mocker):
    with app.app_context():
        unwrangled_labware_spy = mocker.spy(cgap_extraction, "get_unwrangled_labware")
        mocker.patch.object(cgap_extraction, "get_study_uuids")
        mocker.patch.object(cgap_extraction, "get_plate_purpose_uuid")
        mocker.patch.object(cgap_extraction, "get_tube_rack_purpose_uuid")
        mocker.patch.object(cgap_extraction, "create_labwares")
        mocker.patch.object(cgap_extraction, "update_wrangled_labware")

        study_uuids = {"heron": "3333", "heron r and d": "5555"}
        cgap_extraction.get_study_uuids.return_value = study_uuids
        cgap_extraction.get_plate_purpose_uuid.return_value = "7777"
        cgap_extraction.get_tube_rack_purpose_uuid.return_value = "9999"
        cgap_extraction.create_labwares.return_value = [
            cgap_extraction.SSResponse("RACK-1", {}, True),
            cgap_extraction.SSResponse("PLTE-1", {}, False),
        ]

        cgap_extraction.run(app)

        cgap_extraction.get_study_uuids.assert_called_with(set(["heron", "heron r and d"]))
        cgap_extraction.get_plate_purpose_uuid.assert_called_once
        cgap_extraction.get_tube_rack_purpose_uuid.assert_called_once
        cgap_extraction.create_labwares.assert_called_once_with(
            unwrangled_labware_spy.spy_return,
            study_uuids=study_uuids,
            plate_purpose_uuids={
                general_helpers.LabwareType.PLATE: "7777",
                general_helpers.LabwareType.TUBE_RACK: "9999",
            },
        )
        cgap_extraction.update_wrangled_labware.assert_called_once_with("cgap_heron", ["RACK-1"])
