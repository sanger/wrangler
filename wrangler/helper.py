import csv
from http import HTTPStatus
from os.path import getsize, isfile, join
from typing import Dict, Tuple

import requests
from flask import current_app as app

from wrangler.db import get_db
from wrangler.exceptions import BarcodeNotFoundError, BarcodesMismatchError, TubesCountError

STATUS_VALIDATION_FAILED = "validation failed"


def parse_tube_rack_csv(tube_rack_barcode: str) -> Dict:
    """Finds and parses a CSV file with the name matching the tube rack barcode passed in.

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

    Raises:
        BarcodeNotFoundError: if the tube rack CSV file is not found

    Returns:
        Dict -- a dict containing the tube rack barcode and the layout with tube barcodes to
        coordinates
    """
    file_to_find = f"{tube_rack_barcode}.csv"
    full_path_to_find = join(app.config["TUBE_RACK_DIR"], file_to_find)

    app.logger.info(f"Finding file: {full_path_to_find}")

    if isfile(full_path_to_find) and getsize(full_path_to_find) > 0:
        app.logger.debug(f"File found: {file_to_find}")

        with open(full_path_to_find) as tube_rack_file:
            tube_rack_csv = csv.reader(tube_rack_file, delimiter=",")
            layout = {}
            for row in tube_rack_csv:
                tube_barcode = row[1].strip()
                if "NO READ" not in tube_barcode:
                    layout[tube_barcode] = row[0].strip()

        tube_rack_dict = {"rack_barcode": tube_rack_barcode, "layout": layout}

        app.logger.debug(tube_rack_dict)

        return tube_rack_dict
    else:
        raise BarcodeNotFoundError(full_path_to_find)


def send_request_to_sequencescape(endpoint: str, body: Dict) -> int:
    """Send a POST request to Sequencescape with the body provided.

    Arguments:
        endpoint {str} -- the endpoint to which to send the request
        body {dict} -- the JSON body to send with the request

    Returns:
        int -- the HTTP status code
    """
    ss_url = f'{app.config["SS_PROTOCOL"]}://{app.config["SS_HOST"]}/{endpoint}'

    app.logger.info(f"Sending POST to {ss_url}")

    headers = {
        "X-Sequencescape-Client-Id": app.config["SS_API_KEY"],
        "Content-Type": "application/vnd.api+json",
    }

    try:
        response = requests.post(ss_url, json=body, headers=headers)

        app.logger.debug(f"Response code from SS: {response.status_code}")

        return response.status_code
    except Exception as e:
        app.logger.exception(e)


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


def wrangle_tubes(tube_rack_barcode: str) -> Dict:
    """The wrangler wrangles with the tube rack barcode provided. If the barcode exists in the MLWH,
    it tries to find and parse a CSV file with the name as the barcode. If the number of tubes in
    the MLWH match the number of tubes in the CSV file a dict is created which is needed to create
    the tube rack, tubes and samples in Sequencecape.

    Arguments:
        tube_rack_barcode {str} -- the tube rack to look for and wrangle with

    Returns:
        Dict -- the body of the request to send to Sequencescape
    """
    app.logger.debug(f"Wrangle with tube rack barcode: {tube_rack_barcode}")

    cursor = get_db()
    cursor.execute(
        f"SELECT * FROM {app.config['MLWH_DB_TABLE']} "
        f"WHERE tube_rack_barcode = '{tube_rack_barcode}'"
    )

    app.logger.debug(f"Number of records found: {cursor.rowcount}")

    # If there are entries in the MLWH table for that barcode, we need to parse the CSV file and
    #   create the dictionary object from the records in the table and CSV file
    if cursor.rowcount > 0:
        results = list(cursor)
        app.logger.debug(results)

        # create a dict with tube barcode as key and supplier sample ID as value
        tube_sample_dict = {row["tube_barcode"]: row["supplier_sample_id"] for row in results}

        tubes_and_coordinates = parse_tube_rack_csv(tube_rack_barcode)

        # we need to compare the count of records in the MLWH with the count of valid
        # tube barcodes in the parsed CSV file - if these are not the same, exit early
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

        app.logger.debug(f"tubes: {tubes}")

        # set size based on the number of rows in the csv file
        size = 48 if cursor.rowcount == 48 else 96

        tube_rack_response = {
            "tube_rack": {"barcode": tube_rack_barcode, "size": size, "tubes": tubes}
        }
        body = {"data": {"attributes": tube_rack_response}}
        app.logger.debug(body)
        return body
    else:
        raise BarcodeNotFoundError("MLWH")


def error_request_body(exception: Exception, tube_rack_barcode: str) -> Dict:
    """Returns a dictionary to be used as the body in a request.

    Arguments:
        exception {Exception} -- the exception which was raised
        tube_rack_barcode {str} -- the barcode of the tube rack in question

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
    app.logger.exception(exception)

    send_request_to_sequencescape(
        app.config["SS_TUBE_RACK_STATUS_ENDPOINT"],
        error_request_body(exception, tube_rack_barcode),
    )

    if type(exception) == BarcodeNotFoundError:
        return {}, HTTPStatus.NO_CONTENT
    else:
        return {"error": f"{type(exception).__name__}"}, HTTPStatus.OK
