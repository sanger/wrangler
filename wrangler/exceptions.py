class DifferentNumTubesLayoutAndDatabase(ValueError):
    message = 'Different number of tubes between csv and mlwh entries'

class DifferentBarcodesLayoutAndDatabase(ValueError):
    message = 'Some tube barcodes from layout not found in mlwh database'


class TubeRackBarcodeNotFoundInDatabase(ValueError):
    message = "Tube rack barcode not found in the MLWH"