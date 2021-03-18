import pytest
from wrangler import create_app


@pytest.fixture
def app():
    app = create_app(test_config_path="config/test.py")
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
