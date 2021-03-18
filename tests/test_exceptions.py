import pytest
from wrangler.exceptions import CsvNotFoundError


def test_CsvNotFoundError():
    with pytest.raises(CsvNotFoundError, match=r".*\[DN123\].*"):
        raise CsvNotFoundError("DN123")
