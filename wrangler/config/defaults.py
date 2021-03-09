from typing import Any, Dict

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
