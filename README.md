# Wrangler

![Docker CI](https://github.com/sanger/wrangler/workflows/Docker%20CI/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/sanger/wrangler/branch/develop/graph/badge.svg)](https://codecov.io/gh/sanger/wrangler)

A micro service to create labware in Sequencescape based on data stored in CSV files and databases.
Currently, the two main features are:

* lookup and parse a CSV file named after a tube rack barcode provided, return the data in the CSV
if found
* determine if a provided barcode is a plate or a tube rack and create the entity in Sequencescape

The routes of the service are:

    Endpoint                           Methods  Rule
    ---------------------------------  -------  ------------------------------
    labware.wrangle                    POST     /wrangle/<labware_barcode>
    racks.get_tubes_from_rack_barcode  GET      /tube_rack/<tube_rack_barcode>
    static                             GET      /static/<path:filename>

## Requirements

* [pyenv](https://github.com/pyenv/pyenv)
* [pipenv](https://pipenv.pypa.io/en/latest/)
* mySQL

## Setup

* Use pyenv or something similar to install the version of python
defined in the `Pipfile`:
  1. `brew install pyenv`
  2. `pyenv install <python_version>`
* Use pipenv to install python packages: `brew install pipenv`
* To install the required packages (and dev packages) run: `pipenv install --dev`

## Running

1. Create a `.env` file with the following contents (or use `.env.example` - rename to `.env`):
    * `FLASK_APP=wrangler`
    * `FLASK_ENV=development`
    * `SETTINGS_PATH=config/development.py`
1. Run the SQL scripts `wrangler/sql/schema_dev.sql` and `wrangler/sql/schema_test.sql` to create
the development and test databases and their tables.
1. Enter the python virtual environment using `pipenv shell`
1. Run the app using `flask run`

__NB:__ When adding or changing environmental variables, remember to exit and re-enter the virtual
environment.

## Testing

Make sure to be in the virtual environment (`pipenv shell`) before running the tests:

1. Update the credentials for your database in the file `config/test.py`
1. Run the tests using `python -m pytest -vvsx` - flags are for verbose, exit early and capture
output

## Type checking

Type checking is done using mypy, to run it, execute `mypy .`

## Contributing

This project uses [black](https://github.com/psf/black) to check for code format, the use it run:
`black .`
