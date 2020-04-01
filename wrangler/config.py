from os import getenv

TUBE_RACK_DIR = getenv("TUBE_RACK_DIR")
MLWH_DB_USER = getenv("MLWH_DB_USER")
MLWH_DB_PASSWORD = getenv("MLWH_DB_PASSWORD")
MLWH_DB_HOST = getenv("MLWH_DB_HOST")
MLWH_DB_PORT = getenv("MLWH_DB_PORT")
MLWH_DB_DBNAME = getenv("MLWH_DB_DBNAME")
MLWH_DB_TABLE = getenv("MLWH_DB_TABLE")
SS_URL_HOST = getenv("SS_URL_HOST")
SS_API_KEY = getenv("SS_API_KEY")

REQUIRED_CONFIG = (
    "TUBE_RACK_DIR",
    "MLWH_DB_USER",
    "MLWH_DB_PASSWORD",
    "MLWH_DB_HOST",
    "MLWH_DB_PORT",
    "MLWH_DB_DBNAME",
    "MLWH_DB_TABLE",
    "SS_URL_HOST",
    "SS_API_KEY",
)

for config in REQUIRED_CONFIG:
    if not eval(config):
        raise ValueError(f"{config} required for Flask application")
