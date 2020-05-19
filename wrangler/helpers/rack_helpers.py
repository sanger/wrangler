import csv
import logging
from os.path import join
from typing import Any, Dict, List

from flask import current_app as app

from wrangler.exceptions import BarcodesMismatchError, TubesCountError

logger = logging.getLogger(__name__)


def parse_tube_rack_csv(tube_rack_barcode: str) -> Dict[str, Any]:
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
        Optional[Dict[str, str]] -- a dict containing the tube rack barcode and the layout with
        tube barcodes to coordinates
    """
    filename = f"{tube_rack_barcode}.csv"
    full_path_to_file = join(app.config["TUBE_RACK_DIR"], filename)

    with open(full_path_to_file) as tube_rack_file:
        tube_rack_csv = csv.reader(tube_rack_file, delimiter=",")
        layout = {}
        for row in tube_rack_csv:
            tube_barcode = row[1].strip()
            if "NO READ" not in tube_barcode:
                layout[tube_barcode] = row[0].strip()

    tube_rack_dict = {"rack_barcode": tube_rack_barcode, "layout": layout}

    return tube_rack_dict


def validate_tubes(layout_dict: Dict, database_dict: Dict) -> bool:
    """Validates that the number of tubes in the tube rack CSV file are the same as those in the
    MLWH.

    Arguments:
        layout_dict {Dict} -- the dictionary of tube barcodes and coordinates from the tube rack CSV
        database_dict {Dict} -- the dictionary of the database records for the tube rack from the
                                MLWH

    Raises:
        TubesCountError: [description]
        BarcodesMismatchError: [description]

    Returns:
        [boolean] -- returns True if the validation succeeds
    """
    tubes_layout = list(layout_dict.keys())
    tubes_database = list(database_dict.keys())

    if len(tubes_layout) != len(tubes_database):
        raise TubesCountError()
    if len(set(tubes_layout) - set(tubes_database)) != 0:
        raise BarcodesMismatchError()

    return True


def wrangle_tube_rack(
    tube_rack_barcode: str,
    tubes_and_coordinates: Dict[str, Any],
    mlwh_results: List[Dict[str, str]],
) -> Dict[str, Dict[str, Any]]:
    # create a dict with tube barcode as key and supplier sample ID as value
    tube_sample_dict = {row["tube_barcode"]: row["supplier_sample_id"] for row in mlwh_results}

    # we need to compare the count of records in the MLWH with the count of valid tube barcodes in
    #   the parsed CSV file - if these are not the same, exit early
    validate_tubes(tubes_and_coordinates["layout"], tube_sample_dict)

    tubes = []
    for tube_barcode, coordinate in tubes_and_coordinates["layout"].items():
        tubes.append(
            {
                "coordinate": coordinate,
                "barcode": tube_barcode,
                "supplier_sample_id": tube_sample_dict[tube_barcode],
            }
        )

    logger.debug(f"tubes: {tubes}")

    # set size based on the number of rows in the CSV file
    size = 48 if len(mlwh_results) == 48 else 96

    return create_tube_rack_body(size, tube_rack_barcode, tubes)


def create_tube_rack_body(
    size: int, tube_rack_barcode: str, tubes: List[Dict[str, str]]
) -> Dict[str, Dict[str, Any]]:
    tube_rack_response = {"tube_rack": {"barcode": tube_rack_barcode, "size": size, "tubes": tubes}}

    body = {"data": {"attributes": tube_rack_response}}

    logger.debug(body)

    return body
