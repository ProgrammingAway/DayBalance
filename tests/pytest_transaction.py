#!/usr/bin/env python
from app import create_app, db
from app.models import User, Transaction
from config import Config
from datetime import date
import pytest


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'
    START_MONDAY = True


@pytest.fixture
def setup_db():
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    yield
    # Tear Down
    db.session.remove()
    db.drop_all()
    self.app_context.pop()


@pytest.fixture
def db_one_user(setup_db):
    setup_db()
    u = User(username='Panda')
    u.set_password('password')
    u.email = 'panda@email.com'
    u.start_date = date(2021, 1, 1)
    u.set_start_balance(1234.56)
    db.session.add(u)
    db.session.commit()
    yield
    
@pytest.fixture
def db_two_user(db_one_user):
    add_user_1()
    u = User(username='Oreo')
    u.set_password('password2')
    u.email = 'oreo@email.com'
    u.start_date = date(2021, 2, 1)
    u.set_start_balance(6543.21)
    db.session.add(u)
    db.session.commit()
    yield

def createTestTransaction(
    user_id,
    title='Test Transaction',
    date=datetime.now(),
    amount=100.00,
    income=False,
    is_recurring=False,
):
    t = Transaction(user_id=user_id, title=title, date=date, income=income, is_recurring=is_recurring)
    t.set_amount(amount)
    db.session.add(t)
    db.session.commit()
    return Transaction.query.filter_by(id=t.id).first()

def test_amount(db_one_user):
    db_one_user()
    user1 = User.query.filter_by(username='Panda').first()
    t = self.createTestTransaction(user_id=user1.id)
    t.set_amount(123.45)
    self.assertEqual(12345, t.amount)
    t.amount = 54321
    self.assertEqual(543.21, t.return_amount())

def test_byweekday(db_one_user):
    db_one_user()
    user1 = User.query.filter_by(username='Panda').first()
    t = self.createTestTransaction(user_id=user1.id)
    t.set_byweekday(["sun"])
    self.assertTrue(t.day["sun"])
    self.assertFalse(t.day["mon"])
    t.day = {"mon":True, "sun":False}
    byweekday = t.return_byweekday()
    self.assertIn("mon", byweekday)
    self.assertNotIn("sun", byweekday)
    self.assertNotIn("wed", byweekday)
