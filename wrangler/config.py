from os import getenv

MLWH_DB_DBNAME = getenv("MLWH_DB_DBNAME")
MLWH_DB_HOST = getenv("MLWH_DB_HOST")
MLWH_DB_PASSWORD = getenv("MLWH_DB_PASSWORD")
MLWH_DB_PORT = getenv("MLWH_DB_PORT")
MLWH_DB_TABLE = getenv("MLWH_DB_TABLE")
MLWH_DB_USER = getenv("MLWH_DB_USER")
SS_API_KEY = getenv("SS_API_KEY")
SS_HOST = getenv("SS_HOST")
SS_PROTOCOL = getenv("SS_PROTOCOL")
SS_TUBE_RACK_ENDPOINT = getenv("SS_TUBE_RACK_ENDPOINT")
SS_TUBE_RACK_STATUS_ENDPOINT = getenv("SS_TUBE_RACK_STATUS_ENDPOINT")
TUBE_RACK_DIR = getenv("TUBE_RACK_DIR")

REQUIRED_CONFIG = (
    "MLWH_DB_DBNAME",
    "MLWH_DB_HOST",
    "MLWH_DB_PASSWORD",
    "MLWH_DB_PORT",
    "MLWH_DB_TABLE",
    "MLWH_DB_USER",
    "SS_API_KEY",
    "SS_HOST",
    "SS_PROTOCOL",
    "SS_TUBE_RACK_ENDPOINT",
    "SS_TUBE_RACK_STATUS_ENDPOINT",
    "TUBE_RACK_DIR",
)

for config in REQUIRED_CONFIG:
    if not eval(config):
        raise ValueError(f"{config} required for Flask application")
