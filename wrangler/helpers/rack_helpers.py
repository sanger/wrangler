import csv
import logging
from os.path import join
from typing import Any, Dict, Tuple

from flask import current_app as app

logger = logging.getLogger(__name__)


def parse_tube_rack_csv(tube_rack_barcode: str) -> Tuple[int, Dict[str, Any]]:
    """Parses a CSV file with the name matching the tube rack barcode passed in.
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

    Returns:
        Tuple[int, Dict[str, Any]] -- the number of rows in the CSV and a dict containing the tube
        rack barcode along with a layout with tube barcodes to coordinates/position
    """
    filename = f"{tube_rack_barcode}.csv"
    full_path_to_file = join(app.config["TUBE_RACK_DIR"], filename)

    with open(full_path_to_file) as tube_rack_file:
        csv_reader = csv.reader(tube_rack_file, delimiter=",")
        csv_list = list(csv_reader)
        csv_rows = len(csv_list)

        logger.debug(f"{csv_rows} rows in {filename}")

        layout = {}
        for row in csv_list:
            tube_barcode = row[1].strip()
            if "NO READ" not in tube_barcode:
                layout[tube_barcode] = row[0].strip()

    logger.info(f"{filename} parsed successfully")

    tube_rack_dict = {"rack_barcode": tube_rack_barcode, "layout": layout}

    return csv_rows, tube_rack_dict
