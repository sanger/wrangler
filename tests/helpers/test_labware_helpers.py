import pytest

from wrangler.exceptions import IndeterminableLabwareError
from wrangler.helpers.labware_helpers import wrangle_labware


def test_wrangle_labware_indeterminable(app):
    def test_indeterminable_wrangle(app, client):
        with app.app_context():
            with pytest.raises(IndeterminableLabwareError):
                wrangle_labware("indeterminable")
