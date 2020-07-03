import csv
import logging
from os.path import join
from typing import Any, Dict, List, Tuple, Union

from flask import current_app as app

from wrangler.exceptions import BarcodesMismatchError, TubesCountError
from wrangler.helpers.general_helpers import send_request_to_sequencescape
from wrangler.helpers.sample_helpers import sample_contents_for

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

        layout = {}
        for row in csv_list:
            tube_barcode = row[1].strip()
            if "NO READ" not in tube_barcode:
                layout[tube_barcode] = row[0].strip()

    logger.info(f"{filename} parsed successfully")

    tube_rack_dict = {"rack_barcode": tube_rack_barcode, "layout": layout}

    return csv_rows, tube_rack_dict


def validate_tubes(
    tube_rack_barcode: str, layout_tube_barcodes: List[str], db_tube_barcodes: List[str]
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

    if len(layout_tube_barcodes) != len(db_tube_barcodes):
        raise TubesCountError(tube_rack_barcode)

    if set(layout_tube_barcodes) != set(db_tube_barcodes):
        raise BarcodesMismatchError(tube_rack_barcode)

    return True


def create_tube_rack_body(
    tube_rack_barcode: str, mlwh_results: List[Dict[str, str]], purpose_uuid: str, study_uuid: str,
):
    tubes = {}

    for row in mlwh_results:
        tubes[row["position"]] = {
            "barcode": row["tube_barcode"],
            "content": sample_contents_for(row),
        }

    tube_rack_attributes = {
        "barcode": tube_rack_barcode,
        "purpose_uuid": purpose_uuid,
        "study_uuid": study_uuid,
        "tubes": tubes,
    }
    body = {"data": {"attributes": tube_rack_attributes}}

    logger.debug(f"Body to send to SS: {body}")

    return body


def create_tube_rack(tube_rack_body: Dict[str, Union[str, Dict]]):
    return send_request_to_sequencescape(app.config["SS_TUBE_RACK_ENDPOINT"], tube_rack_body)
