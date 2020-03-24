from wrangler import create_app


def test_config():
    # skipping test until we know how to use it with Docker and GitHub actions...
    # assert not create_app().testing
    assert create_app({"TESTING": True}).testing
