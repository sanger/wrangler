import logging
from typing import Any, Dict

from flask import current_app as app

from wrangler.constants import PLATE, TUBE_RACK
from wrangler.db import get_db
from wrangler.exceptions import BarcodeNotFoundError
from wrangler.helpers.general_helpers import csv_file_exists, determine_labware_type
from wrangler.helpers.plate_helpers import create_plate_body
from wrangler.helpers.rack_helpers import parse_tube_rack_csv, wrangle_tube_rack

logger = logging.getLogger(__name__)


def wrangle_labware(labware_barcode: str) -> Dict[str, Any]:
    """The wrangler wrangles with the labware barcode provided. It looks for a CSV file with that
    barcode and retrieves any data for that barcode in the MLWH table.

    If a CSV file exists and matches the data for a tube rack, a new tube rack request is sent to
    Sequencescape. If the data does not match, a new tube rack status request is sent to
    Sequencescape.

    If there is no CSV file but the data looks like a tube rack (tube barcode is populated for all
    records), a tube rack status request is sent to Sequencescape with the error(s).

    If there is no CSV file but the data looks like a plate (tube barcode is null for all records),
    a new plate request is sent to Sequencescape.

    Arguments:
        labware_barcode {str} -- the labware to look for and wrangle with

    Returns:
        Dict -- the body of the request to send to Sequencescape
    """
    logger.info(f"Wrangle with labware barcode: {labware_barcode}")

    # find and parse CSV file if it exists
    csv_exists = csv_file_exists(f"{labware_barcode}.csv")
    if csv_exists:
        tubes_and_coordinates = parse_tube_rack_csv(labware_barcode)

    # get data from the MLWH for the barcode
    cursor = get_db()
    cursor.execute(
        f"SELECT * FROM {app.config['MLWH_DB_TABLE']} "
        f"WHERE container_barcode = '{labware_barcode}'"
    )

    logger.debug(f"Number of records found: {cursor.rowcount}")

    # if there is data in the MLWH, we need to determine what type of labware it is
    if cursor.rowcount > 0:
        results = list(cursor)

        logger.debug(results)

        labware_type = determine_labware_type(results)

        if csv_exists and labware_type == TUBE_RACK:
            return wrangle_tube_rack(labware_barcode, tubes_and_coordinates, results)

        if not csv_exists and labware_type == PLATE:
            return create_plate_body(labware_barcode, results)

        return {}
    else:
        raise BarcodeNotFoundError("MLWH")
