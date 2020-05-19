import logging
from http import HTTPStatus
from os.path import getsize, isfile, join
from typing import Any, Dict, List, Tuple

import requests
from flask import current_app as app

from wrangler.constants import PLATE, STATUS_VALIDATION_FAILED, TUBE_RACK
from wrangler.exceptions import BarcodeNotFoundError, IndeterminableLabwareError

logger = logging.getLogger(__name__)


def csv_file_exists(filename: str) -> bool:
    """Check of the CSV file exists.

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
        logger.warning(f"File not found: {filename}")

        return False


def send_request_to_sequencescape(
    endpoint: str, body: Dict[str, Any]
) -> Tuple[Dict[str, str], int]:
    """Send a POST request to Sequencescape with the body provided.

    Arguments:
        endpoint {str} -- the endpoint to which to send the request
        body {dict} -- the JSON body to send with the request

    Returns:
        int -- the HTTP status code
    """
    ss_url = f'http://{app.config["SS_HOST"]}{endpoint}'

    logger.info(f"Sending POST to {ss_url}")

    headers = {
        "X-Sequencescape-Client-Id": app.config["SS_API_KEY"],
        "Content-Type": "application/vnd.api+json",
    }

    response = requests.post(ss_url, json=body, headers=headers)

    logger.debug(f"Response code from SS: {response.status_code}")

    return response.json(), response.status_code


def get_entity_uuid(entity: str, entity_name: str) -> str:
    """Gets an entity's UUID from Sequencescape.

    Arguments:
        entity {str} -- the entity in question, e.g. 'study'
        entity_name {str} -- the name of a particular entity to search for, e.g. 'Heron'

    Returns:
        str -- the UUID of the entity
    """
    headers = {
        "X-Sequencescape-Client-Id": app.config["SS_API_KEY"],
        "Content-Type": "application/vnd.api+json",
    }

    response = requests.get(
        f"http://{app.config['SS_HOST']}/api/v2/{entity}?filter[name]={entity_name}",
        headers=headers,
    )
    uuid = response.json()["data"]["attributes"]["uuid"]

    return uuid


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
) -> Tuple[Dict[str, str], HTTPStatus]:
    """Handle the exception raised by logging it and creating a status record in SS for the specific
    entity.

    Arguments:
        exception {Exception} -- the exception raised
        labware_barcode {str} -- the barcode of the labware in question
        endpoint {str} -- where to create the status entity record

    Returns:
        Tuple[Dict[str, str], HTTPStatus] -- this gets returned by the Flask view and is converted
        to a Flask Response object
    """
    logger.exception(exception)

    send_request_to_sequencescape(endpoint, error_request_body(exception, labware_barcode))

    if type(exception) == BarcodeNotFoundError:
        return {}, HTTPStatus.NO_CONTENT
    else:
        return {"error": f"{type(exception).__name__}"}, HTTPStatus.OK


def determine_labware_type(records: List[Dict[str, str]]) -> str:
    """Determine the type of labware in the MLWH table by inspecting the records.

    * If all the records have a tube barcode, assume it is a tube rack
    * If all the records' tube barcode field is empty, assume it is a plate

    Arguments:
        records {List[Dict[str, str]]} -- records from the MLWH

    Raises:
        IndeterminableLabwareError: when the labware type is not discernable

    Returns:
        str -- labware type
    """
    if all([record["tube_barcode"] for record in records]):
        return TUBE_RACK

    if len(list(filter(lambda record: record["tube_barcode"] is not None, records))) == 0:
        return PLATE

    raise IndeterminableLabwareError
