import logging
from http import HTTPStatus
from typing import Dict, Tuple

from flask import Blueprint

from wrangler.exceptions import CsvNotFoundError
from wrangler.helpers.general_helpers import csv_file_exists
from wrangler.helpers.rack_helpers import parse_tube_rack_csv

bp = Blueprint("racks", __name__)
logger = logging.getLogger(__name__)


@bp.route("/tube_rack/<tube_rack_barcode>")
def get_tubes_from_rack_barcode(tube_rack_barcode: str) -> Tuple[Dict[str, str], int]:
    """A Flask route which expects a tube rack barcode and returns the tubes in the rack with
    their coordinates.

    Arguments:
        tube_rack_barcode {str} -- the barcode on the tube rack

    Raises:
        CsvNotFoundError: raised when the CSV file is not found for this barcode

    Returns:
        Dict -- a dict with the results or description of the error with "error" as the key
    """
    try:
        logger.info(f"Looking for tube rack with barcode '{tube_rack_barcode}'")
        if not csv_file_exists(f"{tube_rack_barcode}.csv"):
            raise CsvNotFoundError(tube_rack_barcode)

        return parse_tube_rack_csv(tube_rack_barcode), HTTPStatus.OK
    except CsvNotFoundError as e:
        logger.exception(e)

        return {}, HTTPStatus.NO_CONTENT
    except Exception as e:
        logger.exception(e)

        return (
            {"error": f"Server error: {type(e).__name__}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
