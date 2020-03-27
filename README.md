# Tube rack wrangler

![Docker CI](https://github.com/sanger/tube_rack_wrangler/workflows/Docker%20CI/badge.svg)

A micro service to deal with tube racks. Currently, the two main features are:

* lookup and parse a CSV file named after the tube rack barcode
* determine if a tube rack is part of project Heron and if so, request Sequencescape to create
samples

## Requirements

* python 3
* pipenv
* mySQL

## Setup

* To install the required packages run `pipenv install --dev`

## Running

1. Create a `.env` file with the following contents:
    * `FLASK_ENV=development`
    * `FLASK_APP=wrangler`
    * `TUBE_RACK_DIR=<dir>`
    * `MLWH_DB_USER`
    * `MLWH_DB_PASSWORD`
    * `MLWH_DB_HOST`
    * `MLWH_DB_PORT`
    * `MLWH_DB_DBNAME`
    * `MLWH_DB_TABLE`
    * `SS_URL_HOST`
    * `SS_API_KEY=123`

1. Enter the python virtual environment using `pipenv shell`
1. Run the app using `flask run`

## Testing

Make sure to be in virtual environment before running the tests:

1. Create a database locally called 'mlwarehouse_test' and a table in it called 'heron'
1. Update the credentials for your database in the file tests/conftest.py
1. Run the tests using `python -m pytest`
