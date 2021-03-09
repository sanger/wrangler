# flake8: noqa
from wrangler.config.defaults import *

# settings here overwrite those in 'defaults.py'

# tube rack CSV details
TUBE_RACK_DIR = "tests/files"

# logging config
LOGGING["loggers"]["wrangler"]["level"] = "DEBUG"
LOGGING["loggers"]["wrangler"]["handlers"] = ["colored_stream"]
