import pytest
import responses

from wrangler import create_app


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "TUBE_RACK_DIR": "./tests/csvs",
            "MLWH_DB_USER": "root",
            "MLWH_DB_PASSWORD": "root",
            "MLWH_DB_HOST": "localhost",
            "MLWH_DB_PORT": 3306,
            "MLWH_DB_DBNAME": "mlwarehouse_test",
            "SS_URL_HOST": "http://example.com",
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps
