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
        default_message = "TubesCountError: Different number of tubes between CSV and MLWH entries"

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
            "BarcodesMismatchError: Some tube barcodes from the tube rack CSV are not found in "
            "MLWH database"
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


class CsvNotFoundError(Error):
    """Raised when a CSV file named after a tube rack barcode is not found in the NFS.

    Attributes:
        location -- where the barcode was expected to be
        message -- the extra message to be added to the exception
    """

    def __init__(self, tube_rack_barcode, message=None):
        self.message = message
        self.tube_rack_barcode = tube_rack_barcode

    def __str__(self):
        default_message = f"CsvNotFoundError: CSV file not found for {self.tube_rack_barcode}"

        if self.message:
            return f"{default_message}: {self.message}"
        else:
            return default_message


class IndeterminableLabwareError(Error):
    """Raised when the labware is indeterminable from the data stored in the MLWH table.

    Attributes:
        message -- the extra message to be added to the exception
    """

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        default_message = "IndeterminableLabwareError"

        if self.message:
            return f"{default_message}: {self.message}"
        else:
            return default_message
