#!/usr/bin/env python
from datetime import datetime, timedelta, date
import decimal
import unittest
from app import create_app, db
from app.models import User, Transaction
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'
    START_MONDAY = True

class TransactionModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def createTestUser(
        self,
        username='name',
        password='password',
        email='name@email.com',
        start_date=datetime.now(),
        start_balance=100.00,
    ):
        u = User(username=username)
        u.set_password(password)
        u.email = email
        u.start_date = start_date
        u.set_start_balance(start_balance)
        db.session.add(u)
        db.session.commit()
        return User.query.filter_by(id=u.id).first()

    def createTestTransaction(
        self,
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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_amount(self):
        t = self.createTestTransaction(user_id=1)
        t.set_amount(123.45)
        self.assertEqual(12345, t.amount)
        t.amount = 54321
        self.assertEqual(543.21, t.return_amount())

    def test_byweekday(self):
        t = self.createTestTransaction(user_id=1)
        t.set_byweekday(["sun"])
        self.assertTrue(t.day["sun"])
        self.assertFalse(t.day["mon"])
        t.day = {"mon":True, "sun":False}
        byweekday = t.return_byweekday()
        self.assertIn("mon", byweekday)
        self.assertNotIn("sun", byweekday)
        self.assertNotIn("wed", byweekday)

if __name__ == '__main__':
        unittest.main(verbosity=2)
