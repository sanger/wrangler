import os

import pytest
import responses

from wrangler import create_app
from wrangler.db import get_db, get_db_connection, init_db
from wrangler.constants import (
    STUDY_ENTITY, STUDY_HERON, PLATE_PURPOSE_ENTITY,
    PLATE_PURPOSE_STOCK, RACK_PURPOSE_48, RACK_PURPOSE_96
)
from http import HTTPStatus


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

def mock_ss_path_with_uuid(app, mocked_responses, path, uuid):
    ss_url = f'http://{app.config["SS_HOST"]}'
    mocked_responses.add(
        responses.GET,
        f"{ss_url}{path}",
        body=f'{{"data":{{"attributes": {{"uuid":"{uuid}"}}}}}}',
        status=HTTPStatus.OK,
    )


@pytest.fixture
def mocked_ss_calls_for_48_rack(app, mocked_responses):
    mock_ss_path_with_uuid(app,
        mocked_responses,
        f"/api/v2/{STUDY_ENTITY}?filter[name]={STUDY_HERON}",
        "study_heron_uuid"
    )
    mock_ss_path_with_uuid(app,
        mocked_responses,
        f"/api/v2/{PLATE_PURPOSE_ENTITY}?filter[name]={RACK_PURPOSE_48}",
        "purpose_rack_48_uuid"
    )
    yield mocked_responses

@pytest.fixture
def mocked_ss_calls_for_96_rack(app, mocked_responses):
    mock_ss_path_with_uuid(app,
        mocked_responses,
        f"/api/v2/{STUDY_ENTITY}?filter[name]={STUDY_HERON}",
        "study_heron_uuid"
    )
    mock_ss_path_with_uuid(app,
        mocked_responses,
        f"/api/v2/{PLATE_PURPOSE_ENTITY}?filter[name]={RACK_PURPOSE_96}",
        "purpose_rack_96_uuid"
    )
    yield mocked_responses

@pytest.fixture
def mocked_ss_calls_for_plate(app, mocked_responses):
    mock_ss_path_with_uuid(app,
        mocked_responses,
        f"/api/v2/{STUDY_ENTITY}?filter[name]={STUDY_HERON}",
        "study_heron_uuid"
    )
    mock_ss_path_with_uuid(app,
        mocked_responses,
        f"/api/v2/{PLATE_PURPOSE_ENTITY}?filter[name]={PLATE_PURPOSE_STOCK}",
        "purpose_plate_uuid"
    )
    yield mocked_responses



