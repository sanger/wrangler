from os import getenv

TUBE_RACK_DIR = getenv('TUBE_RACK_DIR')

if not TUBE_RACK_DIR:
    raise ValueError("No TUBE_RACK_DIR set for Flask application")
