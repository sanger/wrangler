import logging
from enum import Enum
from http import HTTPStatus
from os.path import getsize, isfile, join
from typing import Any, Dict, Tuple, List

import requests
from flask import current_app as app

from wrangler.constants import (
    STATUS_VALIDATION_FAILED,
    EXTRACT_TR_PURPOSE_96,
    LYSATE_TR_PURPOSE,
    EXTRACT_PLATE_PURPOSE,
    LYSATE_PLATE_PURPOSE
)
from wrangler.exceptions import (
    BarcodeNotFoundError,
    IndeterminableLabwareError,
    IndeterminableSampleTypeError,
    IndeterminablePurposeError
)
from wrangler.utils import pretty

logger = logging.getLogger(__name__)

SS_HEADERS = {
    "Content-Type": "application/vnd.api+json",
}


def csv_file_exists(filename: str) -> bool:
    """Check if the CSV file exists.

    Arguments:
        filename {str} -- the name of the file to check (with extension)

    Returns:
        bool -- whether the file exists or not
    """
    full_path_to_find = join(app.config["TUBE_RACK_DIR"], filename)

    logger.debug(f"Finding file: {full_path_to_find}")

    if isfile(full_path_to_find) and getsize(full_path_to_find) > 0:
        logger.info(f"File found: {filename}")

        return True
    else:
        logger.warning(f"File not found: {full_path_to_find}")

        return False


def send_request_to_sequencescape(
    endpoint: str, body: Dict[str, Any]
) -> Tuple[Dict[str, str], int]:
    """Send a POST request to Sequencescape with the body provided.

    Arguments:
        endpoint {str} -- the endpoint to which to send the request
        body {Dict[str, Any]} -- the body to send with the request

    Returns:
        Tuple[Dict[str, str], int] -- the body in JSON and the status code of the response from
        Sequencescape
    """
    url = f'http://{app.config["SS_HOST"]}{endpoint}'

    logger.debug(f"Sending POST to {url}")

    response = requests.post(
        url,
        json=body,
        headers={**SS_HEADERS, "X-Sequencescape-Client-Id": app.config["SS_API_KEY"]},
    )

    status_code = response.status_code
    response_json = response.json()

    logger.info(f"Response code from SS: {status_code}")
    pretty(logger, response_json)

    return response_json, status_code


def get_entity_uuid(entity: str, entity_name: str) -> str:
    """Gets an entity's UUID from Sequencescape.

    Arguments:
        entity {str} -- the entity in question, e.g. 'study'
        entity_name {str} -- the name of a particular entity to search for, e.g. 'Heron'

    Returns:
        str -- the UUID of the entity
    """
    logger.info(f"Getting UUID for '{entity}' - '{entity_name}'")

    url = f"http://{app.config['SS_HOST']}/api/v2/{entity}?filter[name]={entity_name}"

    logger.debug(f"Sending GET to {url}")

    response = requests.get(
        url, headers={**SS_HEADERS, "X-Sequencescape-Client-Id": app.config["SS_API_KEY"]}
    )

    response_json = response.json()

    pretty(logger, response_json)

    return response_json["data"][0]["attributes"]["uuid"]


def error_request_body(exception: Exception, tube_rack_barcode: str) -> Dict:
    """Returns a dictionary to be used as the body in a request.

    Arguments:
        exception {Exception} -- the exception which was raised
        tube_rack_barcode {str} -- the barcode of the labware in question

    Returns:
        Dict -- the body of the request to be sent
    """
    body = {
        "data": {
            "attributes": {
                "tube_rack_status": {
                    "tube_rack": {
                        "barcode": tube_rack_barcode,
                        "status": STATUS_VALIDATION_FAILED,
                        "messages": [str(exception)],
                    }
                }
            }
        }
    }
    return body


def handle_error(
    exception: Exception, labware_barcode: str, endpoint: str
) -> Tuple[Dict[str, str], int]:
    """Handle the exception raised by logging it and creating a status record in SS for the specific
    entity.

    Arguments:
        exception {Exception} -- the exception raised
        labware_barcode {str} -- the barcode of the labware in question
        endpoint {str} -- where to create the status entity record

    Returns:
        Tuple[Dict[str, str], int] -- this gets returned by the Flask view and is converted to a
        Flask Response object
    """
    logger.exception(exception)

    send_request_to_sequencescape(endpoint, error_request_body(exception, labware_barcode))

    if type(exception) == BarcodeNotFoundError:
        return {}, HTTPStatus.NO_CONTENT
    else:
        return (
            {"error": f"{type(exception).__name__}: {str(exception)}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


class LabwareType(Enum):
    TUBE_RACK = 1
    PLATE = 2

class SampleType(Enum):
    EXTRACT = 1
    LYSATE = 2


def determine_labware_type(labware_barcode: str, records: List[Dict[str, str]]) -> LabwareType:
    """Determine the type of labware in the MLWH table by inspecting the records.

    - If all the records have a tube barcode, assume it is a tube rack
    - If all the records' tube barcode field is empty, assume it is a plate

    Arguments:
        labware_barcode {str} -- barcode of the labware we're determining the type of
        records {List[Dict[str, str]]} -- records from the MLWH

    Raises:
        IndeterminableLabwareError: when the labware type is not discernable

    Returns:
        LabwareType -- labware type
    """
    if all([record["tube_barcode"] for record in records]):
        return LabwareType.TUBE_RACK

    if len(list(filter(lambda record: record["tube_barcode"] is not None, records))) == 0:
        return LabwareType.PLATE

    raise IndeterminableLabwareError(labware_barcode)

def determine_sample_type(labware_barcode: str, records: List[Dict[str, str]]) -> SampleType:
    """Determine the type of sample (whether extract or lysed) in the MLWH table by inspecting the records.

    Arguments:
        labware_barcode {str} -- barcode of the labware holding the samples we're determining the type of
        records {List[Dict[str, str]]} -- records from the MLWH

    Raises:
        IndeterminableSampleTypeError: when the sample type is not discernable

    Returns:
        SampleType -- sample type
    """
    # Assuming sample_type will be the same for all wells/tubes within a container
    sample_type = records[0]["sample_state"]

    if sample_type == "Extract":
        return SampleType.EXTRACT

    if sample_type == "Lysate":
        return SampleType.LYSATE

    raise IndeterminableSampleTypeError(labware_barcode)

def determine_purpose_name(labware_barcode: str, labware_type: LabwareType, sample_type: SampleType) -> str:
    """Determine the plate or rack purpose name, from the sample type and labware type.

    Arguments:
        labware_barcode {str} -- barcode of the labware, of which we are setting the purpose
        labware_type {LabwareType} -- enum representing plate or tube rack
        sample_type {SampleType} -- enum representing lysate or extract

    Raises:
        IndeterminablePurposeError: when the purpose is not discernable

    Returns:
        str -- the purpose name
    """
    if labware_type == LabwareType.TUBE_RACK:
        return EXTRACT_TR_PURPOSE_96 if sample_type == SampleType.EXTRACT else LYSATE_TR_PURPOSE

    if  labware_type == LabwareType.PLATE:
        return EXTRACT_PLATE_PURPOSE if sample_type == SampleType.EXTRACT else LYSATE_PLATE_PURPOSE

    raise IndeterminablePurposeError(labware_barcode)