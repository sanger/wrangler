import mysql.connector
from flask import current_app, g


def init_app(app) -> None:
    app.teardown_appcontext(close_db)  # call when cleaning up after returning the response


def init_db() -> None:
    """Currently only being used when testing
    """
    current_app.logger.debug("Initializing db...")
    db = get_db()

    with current_app.open_resource("sql/schema_test.sql") as f:
        for statement in f:
            db.execute(statement)
        get_db_connection().commit()


def get_db():
    if "db_cursor" not in g:
        g.db_connection = mysql.connector.connect(
            user=current_app.config["MLWH_DB_USER"],
            password=current_app.config["MLWH_DB_PASSWORD"],
            host=current_app.config["MLWH_DB_HOST"],
            port=current_app.config["MLWH_DB_PORT"],
            database=current_app.config["MLWH_DB_DBNAME"],
        )
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
