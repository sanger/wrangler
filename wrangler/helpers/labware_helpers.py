import logging
from http import HTTPStatus
from typing import Dict, Tuple

from flask import current_app as app

from wrangler.constants import (
    PLATE_PURPOSE_ENTITY,
    STUDY_ENTITY,
    EXTRACT_PLATE_PURPOSE,
    EXTRACT_TR_PURPOSE_96,
    LYSATE_PLATE_PURPOSE,
    LYSATE_TR_PURPOSE,
)
from wrangler.db import get_db
from wrangler.exceptions import BarcodeNotFoundError, CsvNotFoundError
from wrangler.helpers.general_helpers import (
    csv_file_exists,
    determine_labware_type,
    LabwareType,
    determine_sample_type,
    SampleType,
    determine_purpose_name,
    get_entity_uuid,
)
from wrangler.helpers.plate_helpers import create_plate, create_plate_body
from wrangler.helpers.rack_helpers import (
    create_tube_rack,
    create_tube_rack_body,
    parse_tube_rack_csv,
    validate_tubes,
)
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

        sample_type = determine_sample_type(labware_barcode, results)
        logger.info(f"Determined sample type: {sample_type}")

        purpose_name = determine_purpose_name(labware_barcode, labware_type, sample_type)
        logger.info(f"Determined purpose name: {purpose_name}")

        # Assuming study is the same for all wells/tubes in a container
        study_name = results[0]["study"]
        logger.info(f"Study name: {study_name}")

        if labware_type == LabwareType.TUBE_RACK:
            if csv_file_exists(f"{labware_barcode}.csv"):
                _, tubes_and_coordinates = parse_tube_rack_csv(labware_barcode)
                db_tube_barcodes = [row["tube_barcode"] for row in results]
                validate_tubes(
                    labware_barcode, tubes_and_coordinates["layout"].keys(), db_tube_barcodes
                )

                tube_rack_body = create_tube_rack_body(
                    labware_barcode,
                    results,
                    purpose_uuid=get_entity_uuid(PLATE_PURPOSE_ENTITY, purpose_name),
                    study_uuid=get_entity_uuid(STUDY_ENTITY, study_name),
                )

                return create_tube_rack(tube_rack_body)
            else:
                raise CsvNotFoundError(labware_barcode)

        if labware_type == LabwareType.PLATE:
            plate_body = create_plate_body(
                labware_barcode,
                results,
                purpose_uuid=get_entity_uuid(PLATE_PURPOSE_ENTITY, purpose_name),
                study_uuid=get_entity_uuid(STUDY_ENTITY, study_name),
            )
            return create_plate(plate_body)

        return {}, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        raise BarcodeNotFoundError(labware_barcode)
