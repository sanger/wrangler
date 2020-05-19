import logging
from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app

from wrangler.exceptions import BarcodeNotFoundError, BarcodesMismatchError, TubesCountError
from wrangler.helpers.general_helpers import handle_error
from wrangler.helpers.labware_helpers import wrangle_labware

bp = Blueprint("labware", __name__)
logger = logging.getLogger(__name__)


@bp.route("/wrangle/<labware_barcode>", methods=["POST"])
def wrangle(labware_barcode: str):
    """A Flask route which accepts a labware barcode, then verifies if it exists in a particular
    MLWH table and if so generates a request body to send to Sequencescape. Currently this applies
    to tube racks and plates.

    Arguments:
        labware_barcode {str} -- The barcode of the labware

    Returns:
        Dict -- a dict with the results or description of the error with "error" as the key
    """
    try:
        return wrangle_labware(labware_barcode)
    except (TubesCountError, BarcodesMismatchError) as e:
        return handle_error(e, labware_barcode, app.config["SS_TUBE_RACK_STATUS_ENDPOINT"])
    except BarcodeNotFoundError as e:
        logger.exception(e)
        return (
            {"error": f"{type(e).__name__}"},
            HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        logger.exception(e)
        return (
            {"error": f"Server error: {type(e).__name__}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
