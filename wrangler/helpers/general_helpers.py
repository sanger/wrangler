import logging
from http import HTTPStatus
from os.path import getsize, isfile, join
from typing import Any, Dict, List, Optional, Tuple

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


def send_request_to_sequencescape(endpoint: str, body: Dict[str, Any]) -> Optional[int]:
    """Send a POST request to Sequencescape with the body provided.

    Arguments:
        endpoint {str} -- the endpoint to which to send the request
        body {dict} -- the JSON body to send with the request

    Returns:
        int -- the HTTP status code
    """
    ss_url = f'{app.config["SS_PROTOCOL"]}://{app.config["SS_HOST"]}{endpoint}'

    logger.info(f"Sending POST to {ss_url}")

    headers = {
        "X-Sequencescape-Client-Id": app.config["SS_API_KEY"],
        "Content-Type": "application/vnd.api+json",
    }

    try:
        response = requests.post(ss_url, json=body, headers=headers)

        logger.debug(f"Response code from SS: {response.status_code}")

        return response.status_code
    except Exception as e:
        logger.exception(e)

        return None


def get_entity_uuid(entity: str, entity_name: str) -> str:
    SS_HEADERS = {"X-Sequencescape-Client-Id": app.config["SS_API_KEY"]}

    response = requests.get(
        f"http://{app.config['SS_HOST']}/api/v2/{entity}?filter[name]={entity_name}",
        headers=SS_HEADERS,
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


def handle_error(exception: Exception, tube_rack_barcode: str) -> Tuple[Dict, HTTPStatus]:
    """Handle the execption raised by logging it and sending the error to Sequencescape.

    Arguments:
        exception {Exception} -- the exception raised
        tube_rack_barcode {str} -- the barcode of the tube rack in question

    Returns:
        Tuple[Dict, HTTPStatus] -- this gets returned by the Flask view and is converted to a Flask
        Response object
    """
    logger.exception(exception)

    send_request_to_sequencescape(
        app.config["SS_TUBE_RACK_STATUS_ENDPOINT"],
        error_request_body(exception, tube_rack_barcode),
    )

    if type(exception) == BarcodeNotFoundError:
        return {}, HTTPStatus.NO_CONTENT
    else:
        return {"error": f"{type(exception).__name__}"}, HTTPStatus.OK


def determine_labware_type(records: List[Dict[str, str]]) -> str:
    if all([record["tube_barcode"] for record in records]):
        return TUBE_RACK

    if len(list(filter(lambda record: record["tube_barcode"] is not None, records))) == 0:
        return PLATE

    raise IndeterminableLabwareError
