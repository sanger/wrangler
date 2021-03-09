from wrangler.helpers.general_helpers import csv_file_exists


def test_csv_file_exists(app):
    with app.app_context():
        assert csv_file_exists("DN_48_valid.csv") is True
        assert csv_file_exists("does not exist") is False
