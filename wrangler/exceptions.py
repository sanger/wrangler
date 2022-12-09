from typing import Optional


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class CsvNotFoundError(Error):
    def __init__(self, tube_rack_barcode: str, message: Optional[str] = None):
        """Raised when a CSV file named after a tube rack barcode is not found in the NFS.

        Arguments:
            tube_rack_barcode {str} -- barcode of the tube rack

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.tube_rack_barcode = tube_rack_barcode

    def __str__(self):
        default_message = f"CsvNotFoundError: [{self.tube_rack_barcode}] CSV file not found for tube rack"

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message
