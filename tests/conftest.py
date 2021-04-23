#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app
import app.models
import config
import datetime
import pytest


class TestConfig(config.Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'
    START_MONDAY = True


class TestConfigSun(config.Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'
    START_MONDAY = False


@pytest.fixture(scope="function")
def setup_db():
    app = app.create_app(TestConfig)
    app_context = app.app_context()
    app_context.push()
    app.db.create_all()
    yield
    # Tear Down
    app.db.session.remove()
    app.db.drop_all()
    app_context.pop()

@pytest.fixture(scope="function")
def setup_db_sun():
    app = create_app(TestConfigSun)
    app_context = app.app_context()
    app_context.push()
    app.db.create_all()
    yield
    # Tear Down
    app.db.session.remove()
    app.db.drop_all()
    app_context.pop()

@pytest.fixture(scope="function")
def db_one_user(setup_db):
    setup_db
    u = app.models.User(username='Panda')
    u.set_password('password')
    u.email = 'panda@email.com'
    u.start_date = datetime.date(2021, 1, 1)
    u.set_start_balance(1234.56)
    app.db.session.add(u)
    app.db.session.commit()
    yield
    
@pytest.fixture(scope="function")
def db_one_user_sun(setup_db_sun):
    setup_db_sun
    u = app.models.User(username='Panda')
    u.set_password('password')
    u.email = 'panda@email.com'
    u.start_date =  datetime.date(2021, 1, 1)
    u.set_start_balance(1234.56)
    app.db.session.add(u)
    app.db.session.commit()
    yield
    
@pytest.fixture(scope="function")
def db_two_users(db_one_user):
    db_one_user
    u = app.models.User(username='Oreo')
    u.set_password('password2')
    u.email = 'oreo@email.com'
    u.start_date = datetime.date(2021, 2, 1)
    u.set_start_balance(6543.21)
    app.db.session.add(u)
    app.db.session.commit()
    yield
