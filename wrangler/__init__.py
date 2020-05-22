import logging
import logging.config

from flask import Flask

logger = logging.getLogger(__name__)


def create_app(test_config_path: str = None):
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

    from . import db

    db.init_app(app)

    if app.config.get("ENABLE_SCHEDULER", False):
        from wrangler.jobs import init_scheduler, cgap_extraction

        scheduler = init_scheduler(app)
        scheduler.add_job(cgap_extraction.run, "interval", minutes=2)

    from wrangler.blueprints import racks
    from wrangler.blueprints import labware

    app.register_blueprint(racks.bp)
    app.register_blueprint(labware.bp)

    return app
