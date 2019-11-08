![](https://github.com/sanger/csv-parser/workflows/.github/workflows/ci.yml/badge.svg)

# CSV parser

A micro service to parse CSV files. Currently only parses tube rack barcodes.

## Requirements

- python 3
- pipenv

## Setup

- To install the required packages run `pipenv install --dev`

## Running

1. Create a `.env` file with the following contents:
    - `FLASK_ENV=development`
    - `TUBE_RACK_DIR=<dir>`
1. Enter the python virtual environment using `pipenv shell`
1. Run the app using `flask run`

## Testing

1. Edit the `.env` file to set `TUBE_RACK_DIR` to the root directory `.`
1. Enter the python virtual environment using `pipenv shell`
1. Run the tests using `python -m pytest`
