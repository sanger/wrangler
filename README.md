# Tube rack wrangler

![](https://github.com/sanger/tube_rack_wrangler/workflows/.github/workflows/ci.yml/badge.svg)

A micro service to deal with tube racks. Currently, the two main features are:

* lookup and parse a CSV file named after the tube rack barcode
* determine if a tube rack is part of project Heron and if so, request Sequencescape to create
samples

## Requirements

* python 3
* pipenv

## Setup

* To install the required packages run `pipenv install --dev`

## Running

1. Create a `.env` file with the following contents:
    * `FLASK_ENV=development`
    * `TUBE_RACK_DIR=<dir>`
    * `MLWH_DB_USER`
    * `MLWH_DB_PASSWORD`
    * `MLWH_DB_HOST`
    * `MLWH_DB_PORT`
    * `MLWH_DB_DBNAME`
    * `SS_URL_HOST`

1. Enter the python virtual environment using `pipenv shell`
1. Run the app using `flask run`

## Testing

1. Edit the `.env` file to set `TUBE_RACK_DIR` to the root directory `.`
1. Enter the python virtual environment using `pipenv shell`
1. Run the tests using `python -m pytest`
