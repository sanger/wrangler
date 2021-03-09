# Wrangler

![CI python](https://github.com/sanger/wrangler/workflows/CI%20python/badge.svg)
![CI docker](https://github.com/sanger/wrangler/workflows/CI%20docker/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/sanger/wrangler/branch/develop/graph/badge.svg)](https://codecov.io/gh/sanger/wrangler)

A micro service to lookup and parse a CSV file named after a tube rack barcode provided and return the data in the CSV
if found

The routes of the service are:

    Endpoint                           Methods  Rule
        ---------------------------------  -------  ------------------------------
        racks.get_tubes_from_rack_barcode  GET      /tube_rack/<tube_rack_barcode>
        static                             GET      /static/<path:filename>

## Requirements

* [pyenv](https://github.com/pyenv/pyenv)
* [pipenv](https://pipenv.pypa.io/en/latest/)

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

1. To setup the database and table (schema defined in 'sql/schema.sql'):

        flask init-db

1. Enter the python virtual environment using:

        pipenv shell

1. Run the app using:

        flask run

__NB:__ When adding or changing environmental variables, remember to exit and re-enter the virtual
environment.

## Testing

1. Run the tests using pytest (flags are for verbose, exit early and capture output):

        python -m pytest -vsx

__NB__: Make sure to be in the virtual environment (`pipenv shell`) before running the tests:

## Type checking

Type checking is done using mypy, to run it, execute `mypy .`

## Contributing

This project uses [black](https://github.com/psf/black) to check for code format, the use it run:
`black .`

## Releases

Update `.release-version` with major/minor/patch. On merging a pull request into develop or master, a release will be created with the release version as the tag/name
