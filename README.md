# Wrangler

![CI](https://github.com/sanger/wrangler/workflows/CI/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/sanger/wrangler/branch/develop/graph/badge.svg)](https://codecov.io/gh/sanger/wrangler)

A micro service to lookup and parse a CSV file named after a tube rack barcode provided and return the data in the CSV
if found.

The routes of the service are:

    Endpoint                           Methods  Rule
    ---------------------------------  -------  ------------------------------
    health_check                       GET      /health
    racks.get_tubes_from_rack_barcode  GET      /tube_rack/<tube_rack_barcode>
    static                             GET      /static/<path:filename>

## Table of Contents

<!-- toc -->

- [Requirements for Development](#requirements-for-development)
  * [Configuring Environment](#configuring-environment)
  * [Setup Steps](#setup-steps)
- [Running](#running)
- [Testing](#testing)
  * [Running Tests](#running-tests)
- [Formatting, Linting and Type Checking](#formatting-linting-and-type-checking)
  * [Formatting](#formatting)
  * [Linting](#linting)
  * [Type Checking](#type-checking)
- [Deployment](#deployment)
- [Miscellaneous](#miscellaneous)
  * [Updating the Table of Contents](#updating-the-table-of-contents)

<!-- tocstop -->

## Requirements for Development

The following tools are required for development:

- python (use `pyenv` or something similar to install the python version specified in the `Pipfile`)
- Git hooks are executed using [lefthook](https://github.com/evilmartians/lefthook), install
  lefthook using homebrew and add the pre-commit and pre-push hooks as follows:

      lefthook add pre-commit
      lefthook add pre-push
- [talisman](https://github.com/thoughtworks/talisman) is used as a credentials checker, to ignore
  files which it triggers as false positives, follow the instructions in the git commit output by
  adding the files to be ignore to a `.talismanrc` file and try commit again.

### Configuring Environment

Create a `.env` file (or copy the `.env.example` file) with the following values:

    SETTINGS_PATH=config/development.py

### Setup Steps

1. Create and enter the virtual environment:

        pipenv shell

1. Install the required dependencies:

        pipenv install --dev

## Running

To run the service:

    flask run

## Testing

### Running Tests

To run the test suite:

    python -m pytest -vx

## Formatting, Linting and Type Checking

### Formatting

This project is formatted using [black](https://github.com/psf/black). To run formatting checks,
run:

    pipenv run black .

### Linting

This project is linted using [flake8](https://github.com/pycqa/flake8). To lint the code, run:

    pipenv run flake8

### Type Checking

This project uses static type checking provided by the [mypy](https://github.com/python/mypy)
library, to run manually:

    pipenv run mypy .

## Deployment

This project uses a Docker image as the unit of deployment. The image is created by GitHub actions.
To trigger the creation of a new image, increment the `.release-version` version with the
corresponding change according to [semver](https://semver.org/).

## Miscellaneous

### Updating the Table of Contents

To update the table of contents after adding things to this README you can use the [markdown-toc](https://github.com/jonschlinkert/markdown-toc)
node module. To run:

    npx markdown-toc -i README.md
