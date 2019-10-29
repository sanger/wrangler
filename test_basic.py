import pytest
from flask import g, session
from app import app

def test_get():
	app.testing = True
	client = app.test_client()
	assert client.get('/rack/1234').status_code == 200