"""
Shared pytest fixtures.

All tests run in demo mode (no OpenAI key needed).
Each test gets a fresh in-memory SQLite DB.
"""

import os
os.environ['DEMO_MODE'] = 'true'
os.environ.setdefault('OPENAI_API_KEY', '')

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from config import TestConfig


@pytest.fixture(scope='session')
def app():
    from app import create_app
    application = create_app(TestConfig())
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    from models import db as _db
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def auth_client(app, db):
    """A test client already logged in as a fresh test user."""
    with app.app_context():
        from models import User
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    c = app.test_client()
    c.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123',
    }, follow_redirects=True)
    return c
