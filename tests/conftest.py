#!/usr/bin/env python
from app import create_app, db
from app.models import User, Transaction
from config import Config
from datetime import datetime, date
import pytest


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'
    START_MONDAY = True


class TestConfigSun(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'
    START_MONDAY = False


@pytest.fixture(scope="function")
def setup_db():
    app = create_app(TestConfig)
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield
    # Tear Down
    db.session.remove()
    db.drop_all()
    app_context.pop()

@pytest.fixture(scope="function")
def setup_db_sun():
    app = create_app(TestConfigSun)
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield
    # Tear Down
    db.session.remove()
    db.drop_all()
    app_context.pop()

@pytest.fixture(scope="function")
def db_one_user(setup_db):
    setup_db
    u = User(username='Panda')
    u.set_password('password')
    u.email = 'panda@email.com'
    u.start_date = date(2021, 1, 1)
    u.set_start_balance(1234.56)
    db.session.add(u)
    db.session.commit()
    yield
    
@pytest.fixture(scope="function")
def db_one_user_sun(setup_db_sun):
    setup_db_sun
    u = User(username='Panda')
    u.set_password('password')
    u.email = 'panda@email.com'
    u.start_date = date(2021, 1, 1)
    u.set_start_balance(1234.56)
    db.session.add(u)
    db.session.commit()
    yield
    
@pytest.fixture(scope="function")
def db_two_users(db_one_user):
    db_one_user
    u = User(username='Oreo')
    u.set_password('password2')
    u.email = 'oreo@email.com'
    u.start_date = date(2021, 2, 1)
    u.set_start_balance(6543.21)
    db.session.add(u)
    db.session.commit()
    yield
