import csv
import logging
from os.path import join
from typing import Any, Dict, List, Tuple

from flask import current_app as app

from wrangler.exceptions import BarcodesMismatchError, TubesCountError, UnexpectedRowCountError
from wrangler.helpers.sample_helpers import sample_contents_for
from wrangler.helpers.general_helpers import get_entity_uuid

from wrangler.constants import (
    PLATE_PURPOSE_ENTITY,
    RACK_PURPOSE_48,
    RACK_PURPOSE_96,
    STUDY_ENTITY,
    STUDY_HERON,
)

logger = logging.getLogger(__name__)


def parse_tube_rack_csv(tube_rack_barcode: str) -> Tuple[int, Dict[str, Any]]:
    """Parses a CSV file with the name matching the tube rack barcode passed in.
    ```
    {
        "rack_barcode": "DN123",
        "layout": {
            "TBD123": "A01",
            "TBD124": "A02",
            "TBD125": "A03"
        }
    }
    ```
    Arguments:
        tube_rack_barcode {str} -- the barcode of the tube rack

    Returns:
        Tuple[int, Dict[str, Any]] -- the number of rows in the CSV and a dict containing the tube
        rack barcode along with a layout with tube barcodes to coordinates/position
    """
    filename = f"{tube_rack_barcode}.csv"
    full_path_to_file = join(app.config["TUBE_RACK_DIR"], filename)

    with open(full_path_to_file) as tube_rack_file:
        csv_reader = csv.reader(tube_rack_file, delimiter=",")
        csv_list = list(csv_reader)
        csv_rows = len(csv_list)

        logger.debug(f"{csv_rows} rows in {filename}")

        if csv_rows not in (48, 96):
            raise UnexpectedRowCountError(tube_rack_barcode)

        layout = {}
        for row in csv_list:
            tube_barcode = row[1].strip()
            if "NO READ" not in tube_barcode:
                layout[tube_barcode] = row[0].strip()

    logger.info(f"{filename} parsed successfully")

    tube_rack_dict = {"rack_barcode": tube_rack_barcode, "layout": layout}

    return csv_rows, tube_rack_dict


def validate_tubes(
    tube_rack_barcode: str, layout_dict: Dict[str, Any], database_dict: Dict[str, str]
) -> bool:
    """Validates that the number of tubes in the tube rack CSV file are the same as those in the
    MLWH.

    Arguments:
        layout_dict {Dict[str, Any]} -- the dictionary of tube barcodes and coordinates from the
        tube rack CSV
        database_dict {Dict[str, str]} -- the dictionary of the database records for the tube rack
        from the MLWH

    Raises:
        TubesCountError: if the number of tubes do not match up
        BarcodesMismatchError: if the tube barcodes do not match up

    Returns:
        [boolean] -- returns True if the validation succeeds
    """
    logger.debug("Validating tubes")

    tubes_layout = list(layout_dict.keys())
    tubes_database = list(database_dict.keys())

    if len(tubes_layout) != len(tubes_database):
        raise TubesCountError(tube_rack_barcode)
    if len(set(tubes_layout) - set(tubes_database)) != 0:
        raise BarcodesMismatchError(tube_rack_barcode)

    return True


def wrangle_tube_rack(
    tube_rack_barcode: str,
    tube_rack_size: int,
    tubes_and_coordinates: Dict[str, Any],
    mlwh_results: List[Dict[str, str]],
) -> Dict[str, Dict[str, Any]]:
    # create a dict with tube barcode as key and supplier sample ID as value
    tube_sample_dict = {row["tube_barcode"]: row["supplier_sample_id"] for row in mlwh_results}

    # we need to compare the count of records in the MLWH with the count of valid tube barcodes in
    #   the parsed CSV file - if these are not the same, exit early
    validate_tubes(tube_rack_barcode, tubes_and_coordinates["layout"], tube_sample_dict)

    tubes = {}
    for tube_barcode, coordinate in tubes_and_coordinates["layout"].items():
        tubes[coordinate] = {
            "barcode": tube_barcode,
            "contents": sample_contents_for(tube_sample_dict[tube_barcode]),
        }

    logger.debug(f"Tubes: {tubes}")

    return create_tube_rack_body(tube_rack_size, tube_rack_barcode, tubes)


def create_tube_rack_body(
    tube_rack_size: int, tube_rack_barcode: str, tubes: List[Dict[str, str]]
) -> Dict[str, Dict[str, Any]]:
    purpose_name = RACK_PURPOSE_48 if tube_rack_size == 48 else RACK_PURPOSE_96

    tube_rack_response = {
        "tube_rack": {
            "barcode": tube_rack_barcode,
            "purpose_uuid": get_entity_uuid(PLATE_PURPOSE_ENTITY, purpose_name),
            "study_uuid": get_entity_uuid(STUDY_ENTITY, STUDY_HERON),
            "tubes": tubes,
        }
    }

    body = {"data": {"attributes": tube_rack_response}}

    logger.debug(f"Body to send to SS: {body}")

    return body
