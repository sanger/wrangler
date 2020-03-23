import csv
from os.path import getsize, isfile, join
from typing import Dict

import requests
from flask import current_app as app

from wrangler.db import get_db


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
        ValueError: if the tube rack is not found

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
                layout[row[1].strip()] = row[0].strip()

        tube_rack_dict = {"rack_barcode": tube_rack_barcode, "layout": layout}

        app.logger.debug(tube_rack_dict)

        return tube_rack_dict
    else:
        raise ValueError(f"File NOT found: {full_path_to_find}")


def send_request_to_sequencescape(body: Dict) -> int:
    """Send a POST request to Sequencescape with the body provided.

    Arguments:
        body {Dict} -- the JSON body to send with the request

    Returns:
        int -- the HTTP status code
    """
    ss_url = app.config["SS_URL_HOST"]
    app.logger.debug(f"Sending POST to {ss_url}")

    headers = {
        "X-Sequencescape-Client-Id": app.config['SS_API_KEY'],
    }

    response = requests.post(ss_url, data=body, headers=headers)

    return response.status_code


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
    cursor = get_db()
    cursor.execute(
        f"SELECT * FROM {app.config['MLWH_DB_TABLE']} WHERE tube_rack_barcode = '{tube_rack_barcode}'"
    )

    app.logger.debug(f"Number of records found: {cursor.rowcount}")

    # If there are entries in the MLWH table for that barcode, we need to parse the CSV file and
    #   create the dictionary object from the records in the table and CSV file
    if cursor.rowcount > 0:
        results = list(cursor)
        app.logger.debug(results)

        # create a dict with tube barcode as key and supplier sample ID as value
        tube_sample_dict = {
            row["tube_barcode"]: row["supplier_sample_id"] for row in results
        }

        tubes_and_coordinates = parse_tube_rack_csv(tube_rack_barcode)

        # we need to compare the count of records in the MLWH with the count of valid
        # tube barcodes in the parsed CSV file - if these are not the same, exit early
        tubes = []
        for tube_barcode, coordinate in tubes_and_coordinates["layout"].items():
            app.logger.debug(tube_barcode)
            app.logger.debug(coordinate)
            tubes.append(
                {
                    "coordinate": coordinate,
                    "barcode": tube_barcode,
                    "supplier_sample_id": tube_sample_dict[tube_barcode],
                }
            )
        app.logger.debug(f"tubes: {tubes}")
        tube_rack_response = {
            "tube_rack": {"barcode": tube_rack_barcode, "tubes": tubes}
        }
        body = {"data": {"attributes": tube_rack_response}}
        app.logger.debug(body)
        return body
    else:
        return None
