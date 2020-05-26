from typing import Any, Dict

# MLWH details
MLWH_DB_DBNAME = "mlwarehouse_dev"
MLWH_DB_HOST = "localhost"
MLWH_DB_PASSWORD = "root"
MLWH_DB_PORT = "3306"
MLWH_DB_TABLE = "cgap_heron"
MLWH_DB_USER = "root"

# Sequencescape details
SS_API_KEY = "123"
SS_HOST = "localhost:3000"
SS_TUBE_RACK_ENDPOINT = "/api/v2/heron/tube_racks"
SS_PLATE_ENDPOINT = "/api/v2/heron/plates"
SS_TUBE_RACK_STATUS_ENDPOINT = "/api/v2/heron/tube_rack_statuses"

# tube rack CSV directory
TUBE_RACK_DIR = "/Users/pj5/dev/psd/wrangler/tests/csvs"

# slack details
SLACK_API_TOKEN = ""
SLACK_CHANNEL_ID = ""

# logging config
LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(asctime)-15s %(name)-33s:%(lineno)-3s %(log_color)s%(levelname)-7s %(message)s",
        },
        "verbose": {"format": "%(asctime)-15s %(name)s:%(lineno)s %(levelname)s %(message)s"},
    },
    "handlers": {
        "colored_stream": {
            "level": "DEBUG",
            "class": "colorlog.StreamHandler",
            "formatter": "colored",
        },
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "verbose"},
        "slack": {
            "level": "ERROR",
            "class": "wrangler.utils.SlackHandler",
            "formatter": "verbose",
            "token": "",
            "channel_id": "",
        },
    },
    "loggers": {"wrangler": {"handlers": ["console", "slack"], "level": "INFO", "propagate": True}},
}
