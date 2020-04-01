import os

import pytest
import responses

from wrangler import create_app
from wrangler.db import get_db, get_db_connection, init_db


@pytest.fixture
def app():
    # don't commit changes to following environment variables because tests in builds rely on them
    app = create_app(
        {
            "TESTING": True,
            "TUBE_RACK_DIR": "./tests/csvs",
            "MLWH_DB_USER": "root",
            "MLWH_DB_PASSWORD": "root",
            "MLWH_DB_HOST": "localhost",
            "MLWH_DB_PORT": 3306,
            "MLWH_DB_DBNAME": "mlwarehouse_test",
            "MLWH_DB_TABLE": "heron",
            "SS_URL_HOST": "http://example.com",
            "SS_API_KEY": "123",
        }
    )

    with app.app_context():
        init_db()  # Create the test schema

        # Populate the db with some test data
        with open(os.path.join(os.path.dirname(__file__), "test_data.sql"), "r") as f:
            for statement in f:
                get_db().execute(statement)
            get_db_connection().commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps
