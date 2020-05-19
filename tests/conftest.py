import os

import pytest
import responses

from wrangler import create_app
from wrangler.db import get_db, get_db_connection, init_db


@pytest.fixture
def app():
    app = create_app(test_config_path="config/test.py")

    with app.app_context():
        init_db()  # Create the test schema

        # Populate the db with some test data
        with open(os.path.join(os.path.dirname(__file__), "test_data.sql"), "r") as f:
            for statement in f:
                get_db().execute(statement)
            get_db_connection().commit()

    yield app


@pytest.fixture
def app_db_less():
    app = create_app(test_config_path="config/test.py")
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps
