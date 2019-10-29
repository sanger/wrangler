import pytest
from flask import g, session
from app import app
import sys

def func(x):
	return x + 1

def test_answer():
	assert func(4) == 5

def test_stuff():
	print('HI')


def test_get():
	app.testing = True
	client = app.test_client()
	assert client.get('/rack/1234').status_code == 200