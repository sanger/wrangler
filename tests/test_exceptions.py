import pytest

from wrangler.exceptions import (
    BarcodeNotFoundError,
    BarcodesMismatchError,
    CsvNotFoundError,
    TubesCountError,
    IndeterminableLabwareError,
    IndeterminableSampleTypeError,
    IndeterminablePurposeError
)


def test_BarcodeNotFoundError():
    with pytest.raises(BarcodeNotFoundError, match=r".*\[DN123\].*"):
        raise BarcodeNotFoundError("DN123")


def test_BarcodesMismatchError():
    with pytest.raises(BarcodesMismatchError, match=r".*\[DN123\].*"):
        raise BarcodesMismatchError("DN123")


def test_CsvNotFoundError():
    with pytest.raises(CsvNotFoundError, match=r".*\[DN123\].*"):
        raise CsvNotFoundError("DN123")


def test_TubesCountError():
    with pytest.raises(TubesCountError, match=r".*\[DN123\].*"):
        raise TubesCountError("DN123")

def test_IndeterminableLabwareError():
    with pytest.raises(IndeterminableLabwareError, match=r".*\[DN123\].*"):
        raise IndeterminableLabwareError("DN123")

def test_IndeterminableSampleTypeError():
    with pytest.raises(IndeterminableSampleTypeError, match=r".*\[DN123\].*"):
        raise IndeterminableSampleTypeError("DN123")

def test_IndeterminablePurposeError():
    with pytest.raises(IndeterminablePurposeError, match=r".*\[DN123\].*"):
        raise IndeterminablePurposeError("DN123")
