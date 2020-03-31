from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app

from .exceptions import BarcodeNotFoundError, BarcodesMismatchError, TubesCountError
from .helper import (
    handle_error,
    parse_tube_rack_csv,
    send_request_to_sequencescape,
    wrangle_tubes,
)

bp = Blueprint("racks", __name__)


@bp.route("/tube_rack/<tube_rack_barcode>")
def get_tubes_from_rack_barcode(tube_rack_barcode: str):
    """A Flask route which expects a tube rack barcode and returns the tubes in the rack with
    their coordinates.

    Arguments:
        tube_rack_barcode {str} -- the barcode on the tube rack

    Returns:
        Dict -- a dict with the results or description of the error with "error" as the key
    """
    try:
        return parse_tube_rack_csv(tube_rack_barcode)
    except BarcodeNotFoundError as e:
        app.logger.exception(e)
        return {}, HTTPStatus.NO_CONTENT
    except Exception as e:
        app.logger.exception(e)
        return (
            {"error": f"Server error: {type(e).__name__}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@bp.route("/wrangle/<tube_rack_barcode>")
def wrangle(tube_rack_barcode: str):
    """A Flask route which accepts a tube rack barcode, then verifies if it exists in a particular
    MLWH table and if so generates a request body to send to Sequencescape.

    Arguments:
        tube_rack_barcode {str} -- The barcode of the tube rack

    Returns:
        Dict -- a dict with the results or description of the error with "error" as the key
    """
    try:
        tube_request_body = wrangle_tubes(tube_rack_barcode)
        send_request_to_sequencescape("POST", tube_request_body)
        return "POST request successfully sent to Sequencescape", HTTPStatus.OK
    except (TubesCountError, BarcodesMismatchError, BarcodeNotFoundError) as e:
        return handle_error(e, tube_rack_barcode)
    except Exception as e:
        app.logger.exception(e)
        return (
            {"error": f"Server error: {type(e).__name__}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
