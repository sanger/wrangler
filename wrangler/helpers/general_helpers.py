import logging
from os.path import getsize, isfile, join

from flask import current_app as app

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
