import logging
from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app

from wrangler.helpers.general_helpers import send_request_to_sequencescape
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
        tube_request_body = wrangle_labware(labware_barcode)
        send_request_to_sequencescape(app.config["SS_TUBE_RACK_ENDPOINT"], tube_request_body)
        return "POST request successfully sent to Sequencescape", HTTPStatus.OK
    # except (TubesCountError, BarcodesMismatchError, BarcodeNotFoundError) as e:
    #     return handle_error(e, labware_barcode)
    except Exception as e:
        logger.exception(e)
        return (
            {"error": f"Server error: {type(e).__name__}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
