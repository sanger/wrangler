from wrangler.config.defaults import *  # noqa: F403,F401

# settings here overwrite those in 'defaults.py'
TESTING = True

# MLWH details
MLWH_DB_DBNAME = "mlwarehouse_test"
MLWH_DB_HOST = "172.27.85.88"
MLWH_DB_PASSWORD = ""

# tube rack CSV details
TUBE_RACK_DIR = "tests/files"

# logging config
LOGGING["loggers"]["wrangler"]["level"] = "DEBUG"
LOGGING["loggers"]["wrangler"]["handlers"] = ["colored_stream"]
