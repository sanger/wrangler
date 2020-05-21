import pytest
import responses

from wrangler import create_app


@pytest.fixture
def app():
    app = create_app(test_config_path="config/test.py")

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
