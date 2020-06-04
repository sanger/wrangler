import pytest

from wrangler.exceptions import (
    BarcodeNotFoundError,
    BarcodesMismatchError,
    CsvNotFoundError,
    TubesCountError,
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
