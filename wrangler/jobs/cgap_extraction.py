from collections import namedtuple
from http import HTTPStatus
from itertools import groupby
from typing import List, Dict, Iterable, Generator

from flask import current_app as app

from wrangler.constants import (
    PLATE_PURPOSE_ENTITY,
    HERON_TR_PURPOSE,
    STUDY_ENTITY,
    HERON_PLATE_PURPOSE,
)
from wrangler.db import get_db
from wrangler.helpers.general_helpers import determine_labware_type, get_entity_uuid, LabwareType
from wrangler.helpers.plate_helpers import create_plate, create_plate_body
from wrangler.helpers.rack_helpers import create_tube_rack, create_tube_rack_body

SSResponse = namedtuple("SSResponse", "barcode body successful")


def run():
    """
    This function is designed to be called from a scheduler.
        - It finds a list of containers that need to be created in SequenceScape
        - Looks up required study and plate purpose UUIDs
        - Creates the labware
        - Marks the created labware as "wrangled" in the mlwh
    
    Returns:
        None
    """
    mlwh_rows = get_unwrangled_labware()

    if len(mlwh_rows) == 0:
        return

    # Look up various UUIDs ahead of labware creation, so it only has to happen once
    study_uuids = get_study_uuids({row["study"] for row in mlwh_rows})
    plate_plate_purpose_uuid = get_plate_purpose_uuid()
    rack_plate_purpose_uuid = get_tube_rack_purpose_uuid()

    ss_responses = create_labwares(
        mlwh_rows,
        study_uuids=study_uuids,
        plate_purpose_uuids={
            LabwareType.PLATE: plate_plate_purpose_uuid,
            LabwareType.TUBE_RACK: rack_plate_purpose_uuid,
        },
    )

    for successful, responses in groupby(ss_responses, lambda x: x.successful):
        labware_barcodes = [x.barcode for x in responses]

        if successful:
            update_wrangled_labware(labware_barcodes)
            app.logger.info(
                f"The following labware were successfully created: {','.join(labware_barcodes)}"
            )
        else:
            app.logger.error(
                f"The following labware failed to be created: {','.join(labware_barcodes)}"
            )


def get_unwrangled_labware() -> List[Dict[str, str]]:
    """
    Fetches a list of unwrangled labware from the mlwh.
    Returns:
        A list of labware that needs to be created in SequenceScape.
    """
    query = (
        f"SELECT * FROM {app.config['MLWH_DB_TABLE']} "
        f"WHERE destination = '{app.config['CGAP_EXTRACTION_DESTINATION']}' "
        f"AND wrangled IS NULL "
        f"ORDER BY container_barcode"
    )
    cursor = get_db()
    cursor.execute(query)
    return list(cursor)


def get_study_uuids(studies: Iterable[str]) -> Dict[str, str]:
    """
    Creates a map of study names to their UUIDs.
    Args:
        studies: An iterable of study names to look up

    Returns:
        A dictionary of study name to its UUID
    """
    return {study: get_entity_uuid(STUDY_ENTITY, study) for study in studies}


def get_plate_purpose_uuid() -> str:
    return get_entity_uuid(PLATE_PURPOSE_ENTITY, HERON_PLATE_PURPOSE)


def get_tube_rack_purpose_uuid() -> str:
    return get_entity_uuid(PLATE_PURPOSE_ENTITY, HERON_TR_PURPOSE)


def create_labwares(mlwh_rows, **kwargs) -> Generator:
    """
    Groups labware by its container barcode, then sends a request to create it to SequenceScape.
    Args:
        mlwh_rows: List of rows from the multi-lims warehouse
        **kwargs:
            study_uuids: A dictionary of study names to their UUIDs
            plate_purpose_uuids: A dictionary of labware types to their plate purposes

    Returns:
        Yields a SSResponse for each labware it attempts to create

    """
    for barcode, container_rows_iter in groupby(mlwh_rows, lambda x: x["container_barcode"]):
        container_rows = list(container_rows_iter)
        labware_type = determine_labware_type(barcode, container_rows)

        # Assuming study will be the same for all wells/tubes within a container
        study_uuid = kwargs.get("study_uuids", {}).get(container_rows[0]["study"])

        if labware_type == LabwareType.PLATE:
            labware_body = create_plate_body(
                barcode,
                container_rows,
                study_uuid=study_uuid,
                purpose_uuid=kwargs.get("plate_purpose_uuids", {}).get(LabwareType.PLATE),
            )
            response, status_code = create_plate(labware_body)

        elif labware_type == LabwareType.TUBE_RACK:
            labware_body = create_tube_rack_body(
                barcode,
                container_rows,
                study_uuid=study_uuid,
                purpose_uuid=kwargs.get("plate_purpose_uuids", {}).get(LabwareType.TUBE_RACK),
            )
            response, status_code = create_tube_rack(labware_body)
        else:
            raise Exception(f"cgap extraction job can not handle labware type: {labware_type}")

        yield SSResponse(barcode, response, status_code == HTTPStatus.CREATED)


def update_wrangled_labware(container_barcodes: List[str]):
    """
    Updates the given containers as wrangled by setting the wrangled column to NOW().
    Args:
        container_barcodes: List of container barcodes to set as wrangled.

    Returns:
        A MySQL cursor after having updated the table.
    """
    query = (
        f"UPDATE {app.config['MLWH_DB_TABLE']} SET wrangled = NOW() "
        f"WHERE container_barcode IN ({ ','.join(['%s'] * len(container_barcodes))})"
    )
    cursor = get_db()
    cursor.execute(query, tuple(container_barcodes))
    return cursor
