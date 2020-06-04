class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class TubesCountError(Error):
    def __init__(self, tube_rack_barcode: str, message: str = None):
        """Raised when the number of tubes in the CSV for a tube rack does not equal the number of tubes
        for that tube rack in the MLWH.

        Arguments:
            tube_rack_barcode {str} -- barcode of the tube rack

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.tube_rack_barcode = tube_rack_barcode

    def __str__(self):
        default_message = (
            f"TubesCountError: [{self.tube_rack_barcode}] Different number of tubes between CSV "
            "and MLWH records"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message


class BarcodesMismatchError(Error):
    def __init__(self, tube_rack_barcode: str, message: str = None):
        """Raised when there are tube barcodes present in the tube rack CSV but not in the MLWH.

        Arguments:
            tube_rack_barcode {str} -- barcode of the tube rack

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.tube_rack_barcode = tube_rack_barcode

    def __str__(self):
        default_message = (
            f"BarcodesMismatchError: [{self.tube_rack_barcode}] Some tube barcodes from the tube "
            "rack CSV are not found in the MLWH"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message


class BarcodeNotFoundError(Error):
    def __init__(self, labware_barcode: str, message: str = None):
        """Raised when a labware barcode is not found in the MLWH.

        Arguments:
            labware_barcode {str} -- barcode of the labware

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.labware_barcode = labware_barcode

    def __str__(self):
        default_message = (
            f"BarcodeNotFoundError: [{self.labware_barcode}] Labware barcode not found in the MLWH"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message


class CsvNotFoundError(Error):
    def __init__(self, tube_rack_barcode: str, message: str = None):
        """Raised when a CSV file named after a tube rack barcode is not found in the NFS.

        Arguments:
            tube_rack_barcode {str} -- barcode of the tube rack

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.tube_rack_barcode = tube_rack_barcode

    def __str__(self):
        default_message = (
            f"CsvNotFoundError: [{self.tube_rack_barcode}] CSV file not found for tube rack"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message


class IndeterminableLabwareError(Error):
    def __init__(self, labware_barcode: str, message: str = None):
        """Raised when the labware is indeterminable from the data stored in the MLWH table.

        Arguments:
            labware_barcode {str} -- barcode of the labware

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.labware_barcode = labware_barcode

    def __str__(self):
        default_message = (
            f"IndeterminableLabwareError: [{self.labware_barcode}] Cannot determine the type of "
            "labware from the records in the MLWH"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message


class IndeterminableSampleTypeError(Error):
    def __init__(self, labware_barcode: str, message: str = None):
        """Raised when the sample type is indeterminable from the data stored in the MLWH table.

        Arguments:
            labware_barcode {str} -- barcode of the labware

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.labware_barcode = labware_barcode

    def __str__(self):
        default_message = (
            f"IndeterminableSampleTypeError: [{self.labware_barcode}] Cannot determine the type of "
            "sample (e.g. 'Lysate') from the records in the MLWH"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message


class IndeterminablePurposeError(Error):
    def __init__(self, labware_barcode: str, message: str = None):
        """Raised when the purpose name cannot be determined from the sample type and labware type.

        Arguments:
            labware_barcode {str} -- barcode of the labware

        Keyword Arguments:
            message {str} -- extra message to add to the exception (default: {None})
        """
        self.message = message
        self.labware_barcode = labware_barcode

    def __str__(self):
        default_message = (
            f"IndeterminablePurposeError: [{self.labware_barcode}] Cannot determine the purpose that should "
            "be used, from the sample type and labware type"
        )

        if self.message:
            return f"{default_message} - {self.message}"
        else:
            return default_message
