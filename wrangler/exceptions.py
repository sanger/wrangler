class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class TubesCountError(Error):
    """Raised when the number of tubes in the CSV for a tube rack does no equal the number of tubes
    for that tube rack in the MLWH.
    """

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        default_message = f"TubesCountError: Different number of tubes between CSV and MLWH entries"

        if self.message:
            return f"{default_message}: {self.message}"
        else:
            return default_message


class BarcodesMismatchError(Error):
    """Raised when there are tube barcodes present in the tube rack CSV but not in the MLWH.

    Attributes:
        message -- the extra message to be added to the exception
    """

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        default_message = (
            f"BarcodesMismatchError: Some tube barcodes from the tube rack CSV are not found in "
            f"MLWH database"
        )

        if self.message:
            return f"{default_message}: {self.message}"
        else:
            return default_message


class BarcodeNotFoundError(Error):
    """Raised when a tube rack barcode is not found in a location.

    Attributes:
        location -- where the barcode was expected to be
        message -- the extra message to be added to the exception
    """

    def __init__(self, location, message=None):
        self.message = message
        self.location = location

    def __str__(self):
        default_message = f"BarcodeNotFoundError: Tube rack barcode not found in {self.location}"

        if self.message:
            return f"{default_message}: {self.message}"
        else:
            return default_message
