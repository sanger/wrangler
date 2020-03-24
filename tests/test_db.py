import pytest
from mysql.connector import ProgrammingError

from wrangler.db import get_db, get_db_connection


def test_get_close_db(app):
    with app.app_context():
        db = get_db()

        db_connection = get_db_connection()
        assert db is get_db()

    with pytest.raises(ProgrammingError):
        db.execute("SELECT 1")

    assert db_connection.is_connected() is False
