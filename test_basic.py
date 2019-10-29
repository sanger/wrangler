import pytest
from flask import g, session
from app import app
import json

def test_file_found():
	app.testing = True
	client = app.test_client()
	assert client.get('/rack/test').status_code == 200

def test_file_not_found():
	app.testing = True
	client = app.test_client()
	assert client.get('/rack/574').status_code == 404

def test_valid_file():
	app.testing = True
	client = app.test_client()	
	output = {"rack_barcode": "test", "layout": [{"a1": "test_barcode"}, {"b1": "test_barcode2"}]}
	response = client.get('/rack/test')
	assert response.get_json() == output

def test_invalid_file():
	app.testing = True
	client = app.test_client()	
	response = client.get('/rack/wrong_test')
	assert response.status_code == 500
