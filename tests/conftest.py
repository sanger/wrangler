import pytest
import responses

from wrangler import create_app

from wrangler.constants import (
    STUDY_ENTITY,
    STUDY_HERON,
    PLATE_PURPOSE_ENTITY,
    STOCK_TR_PURPOSE_96,
)
from http import HTTPStatus


def mock_ss_path_with_uuid(app, mocked_responses, path, uuid):
    ss_url = f'http://{app.config["SS_HOST"]}'
    mocked_responses.add(
        responses.GET,
        f"{ss_url}{path}",
        body=f'{{"data": [{{"attributes": {{"uuid":"{uuid}"}}}}] }}',
        status=HTTPStatus.OK,
    )


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


@pytest.fixture
def mocked_ss_calls_for_96_rack(app, mocked_responses):
    mock_ss_path_with_uuid(
        app,
        mocked_responses,
        f"/api/v2/{STUDY_ENTITY}?filter[name]={STUDY_HERON}",
        "study_heron_uuid",
    )
    mock_ss_path_with_uuid(
        app,
        mocked_responses,
        f"/api/v2/{PLATE_PURPOSE_ENTITY}?filter[name]={STOCK_TR_PURPOSE_96}",
        "purpose_rack_96_uuid",
    )
    yield mocked_responses


@pytest.fixture
def mocked_ss_calls_with_study_and_rack_96_purpose(app, mocked_responses):
    mock_ss_path_with_uuid(
        app,
        mocked_responses,
        f"/api/v2/{STUDY_ENTITY}?filter[name]={STUDY_HERON}",
        "study_heron_uuid",
    )
    mock_ss_path_with_uuid(
        app,
        mocked_responses,
        f"/api/v2/{PLATE_PURPOSE_ENTITY}?filter[name]={STOCK_TR_PURPOSE_96}",
        "purpose_rack_96_uuid",
    )
    yield mocked_responses
