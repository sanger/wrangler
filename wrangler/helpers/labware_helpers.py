import logging
from http import HTTPStatus
from typing import Dict, Tuple

from flask import current_app as app

from wrangler.constants import PLATE, TUBE_RACK
from wrangler.db import get_db
from wrangler.exceptions import BarcodeNotFoundError, CsvNotFoundError
from wrangler.helpers.general_helpers import (
    csv_file_exists,
    determine_labware_type,
    send_request_to_sequencescape,
)
from wrangler.helpers.plate_helpers import create_plate_body
from wrangler.helpers.rack_helpers import parse_tube_rack_csv, wrangle_tube_rack

logger = logging.getLogger(__name__)


def wrangle_labware(labware_barcode: str) -> Tuple[Dict[str, str], int]:
    """Wrangles with the provided labware barcode.

    - It first retrieves data from the MLWH for the barcode. If there is data, it determines what
    type of labware it is
        - If the labware is a tube rack, it looks for the CSV file expected for that tube rack
            - If the CSV file is present and valid, it creates and send a new tube rack request to
            Sequencescape
            - If the CSV is not present or fails validation, it raises an exception
        - If the labware is a plate, it creates and sends a request to Sequencescape
    - If there is no data in the MLWH, it raises an exception

    Arguments:
        labware_barcode {str} -- the labware to look for and wrangle with

    Returns:
        Dict -- the body of the request to send to Sequencescape
    """
    logger.info(f"Wrangle with labware barcode: {labware_barcode}")

    # get data from the MLWH for the barcode
    cursor = get_db()
    cursor.execute(
        f"SELECT * FROM {app.config['MLWH_DB_TABLE']} "
        f"WHERE container_barcode = '{labware_barcode}'"
    )

    logger.debug(f"Number of records found: {cursor.rowcount}")

    # if there is data in the MLWH, determine what type of labware it is
    if cursor.rowcount > 0:
        results = list(cursor)

        logger.debug(results)

        labware_type = determine_labware_type(labware_barcode, results)
        logger.info(f"Determined labware type: {labware_type}")

        if labware_type == TUBE_RACK:
            if csv_file_exists(f"{labware_barcode}.csv"):
                tubes_and_coordinates = parse_tube_rack_csv(labware_barcode)
                ss_request_body = wrangle_tube_rack(labware_barcode, tubes_and_coordinates, results)

                return send_request_to_sequencescape(
                    app.config["SS_TUBE_RACK_ENDPOINT"], ss_request_body
                )
            else:
                raise CsvNotFoundError(labware_barcode)

        if labware_type == PLATE:
            ss_request_body = create_plate_body(labware_barcode, results)

            return send_request_to_sequencescape(app.config["SS_PLATE_ENDPOINT"], ss_request_body)

        return {}, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        raise BarcodeNotFoundError(labware_barcode)
