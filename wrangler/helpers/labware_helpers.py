import logging
from http import HTTPStatus
from typing import Dict, Tuple

from flask import current_app as app

from wrangler.constants import (
    PLATE_PURPOSE_ENTITY,
    STOCK_PLATE_PURPOSE,
    STUDY_ENTITY,
    STOCK_TR_PURPOSE_96,
)
from wrangler.db import get_db
from wrangler.exceptions import BarcodeNotFoundError, CsvNotFoundError
from wrangler.helpers.general_helpers import (
    csv_file_exists,
    determine_labware_type,
    LabwareType,
    get_entity_uuid,
)
from wrangler.helpers.plate_helpers import create_plate
from wrangler.helpers.plate_helpers import create_plate_body
from wrangler.helpers.rack_helpers import (
    create_tube_rack,
    create_tube_rack_body,
)
from wrangler.helpers.rack_helpers import parse_tube_rack_csv, wrangle_tube_rack
from wrangler.utils import pretty

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

        pretty(logger, results)

        labware_type = determine_labware_type(labware_barcode, results)
        logger.info(f"Determined labware type: {labware_type}")

        # Assuming study is the same for all wells/tubes in a container
        study_name = results[0]["study"]
        logger.info(f"Study name: {study_name}")

        if labware_type == LabwareType.TUBE_RACK:
            if csv_file_exists(f"{labware_barcode}.csv"):
                tube_rack_size, tubes_and_coordinates = parse_tube_rack_csv(labware_barcode)
                tubes = wrangle_tube_rack(labware_barcode, tubes_and_coordinates, results)

                tube_rack_body = create_tube_rack_body(
                    labware_barcode,
                    tubes,
                    plate_purpose_uuid=get_entity_uuid(PLATE_PURPOSE_ENTITY, STOCK_TR_PURPOSE_96),
                    study_uuid=get_entity_uuid(STUDY_ENTITY, study_name),
                )

                return create_tube_rack(tube_rack_body)
            else:
                raise CsvNotFoundError(labware_barcode)

        if labware_type == LabwareType.PLATE:
            plate_body = create_plate_body(
                labware_barcode,
                results,
                purpose_uuid=get_entity_uuid(PLATE_PURPOSE_ENTITY, STOCK_PLATE_PURPOSE),
                study_uuid=get_entity_uuid(STUDY_ENTITY, study_name),
            )
            return create_plate(plate_body)

        return {}, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        raise BarcodeNotFoundError(labware_barcode)
