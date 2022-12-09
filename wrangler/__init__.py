import logging
import logging.config
from http import HTTPStatus
from typing import Optional

from flask import Flask

logger = logging.getLogger(__name__)


def create_app(test_config_path: Optional[str] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)

    if test_config_path is None:
        # load the config, if it exists, when not testing
        # app.config.from_pyfile("config.py", silent=True)
        app.config.from_envvar("SETTINGS_PATH")
    else:
        # load the test config if passed in
        app.config.from_pyfile(test_config_path)

    # setup logging
    logging.config.dictConfig(app.config["LOGGING"])

    from wrangler.blueprints import racks

    app.register_blueprint(racks.bp)

    @app.route("/health")
    def health_check():
        return "Factory working", HTTPStatus.OK

    return app
