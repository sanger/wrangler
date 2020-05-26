import logging
import os
import pathlib

import click
import mysql.connector  # type: ignore
from flask import current_app, g
from flask.cli import with_appcontext

logger = logging.getLogger(__name__)


def init_app(app) -> None:
    app.teardown_appcontext(close_db)  # call when cleaning up after returning the response
    app.cli.add_command(init_db_command)


def get_db(ignore_database: bool = False):
    if "db_cursor" not in g:
        connection_params = {
            "user": current_app.config["MLWH_DB_USER"],
            "password": current_app.config["MLWH_DB_PASSWORD"],
            "host": current_app.config["MLWH_DB_HOST"],
            "port": current_app.config["MLWH_DB_PORT"],
            "database": current_app.config["MLWH_DB_DBNAME"],
        }

        # remove the database key when connecting to the server to create the databases
        if ignore_database:
            del connection_params["database"]

        g.db_connection = mysql.connector.connect(**connection_params)
        g.db_cursor = g.db_connection.cursor(buffered=True, dictionary=True)

    return g.db_cursor


def get_db_connection():
    return g.db_connection


def close_db(e=None) -> None:
    db_cursor = g.pop("db_cursor", None)
    db_connection = g.pop("db_connection", None)

    if db_cursor is not None:
        db_cursor.close()

    if db_connection is not None:
        db_connection.close()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    click.echo("Initialising the database")

    db = get_db(ignore_database=True)

    with current_app.open_resource("sql/schema.sql", mode="rt") as f:
        template = current_app.jinja_env.from_string(f.read())

    sql_script = template.render(database=current_app.config["MLWH_DB_DBNAME"])

    for result in db.execute(sql_script, multi=True):
        if result.with_rows:
            result.fetchall()

    if current_app.testing:
        click.echo("Inserting test data")

        (_, _, files) = next(os.walk(pathlib.Path(__file__).parent.joinpath("sql/test_data")))
        for filename in files:
            click.echo(f"Processing {filename}")

            with current_app.open_resource(f"sql/test_data/{filename}", mode="rt") as f:
                template = current_app.jinja_env.from_string(f.read())

            sql_script = template.render(database=current_app.config["MLWH_DB_DBNAME"])

            for result in db.execute(sql_script, multi=True):
                if result.with_rows:
                    result.fetchall()

            get_db_connection().commit()

    click.echo("Done")
