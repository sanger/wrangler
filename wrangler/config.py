from os import getenv

TUBE_RACK_DIR = getenv("TUBE_RACK_DIR")
MLWH_DB_USER = getenv("MLWH_DB_USER")
MLWH_DB_PASSWORD = getenv("MLWH_DB_PASSWORD")
MLWH_DB_HOST = getenv("MLWH_DB_HOST")
MLWH_DB_PORT = getenv("MLWH_DB_PORT")
MLWH_DB_DBNAME = getenv("MLWH_DB_DBNAME")
SS_URL_HOST = getenv("SS_URL_HOST")

REQUIRED_CONFIG = (
    "TUBE_RACK_DIR",
    "MLWH_DB_USER",
    "MLWH_DB_PASSWORD",
    "MLWH_DB_HOST",
    "MLWH_DB_PORT",
    "MLWH_DB_DBNAME",
    "SS_URL_HOST",
)

for config in REQUIRED_CONFIG:
    if not eval(config):
        raise ValueError(f"{config} required for Flask application")
