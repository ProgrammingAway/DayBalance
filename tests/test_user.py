#!/usr/bin/env python
from datetime import datetime, timedelta, date
import unittest
from app import create_app, db
from app.models import User, Transaction
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'testing'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def createTestUser(self):
        u = User(username='brian')
        u.set_password('password')
        u.email = 'brian@test.com'
        u.start_date = datetime.now()
        u.start_balance = 10.00
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        #u = User(username='brian')
        #u.set_password('password')
        self.createTestUser()
        u = User.query.filter_by(username='brian').first()
        self.assertFalse(u.check_password('other_password'))
        self.assertTrue(u.check_password('password'))

    def test_token(self):
        #u = User(username='brian')
        #u.set_password('password')
        #u.email = 'brian@test.com'
        #u.start_date = datetime.now()
        #u.start_balance = 10.00
        #db.session.add(u)
        #db.session.commit()
        self.createTestUser()
        u = User.query.filter_by(username='brian').first()
        token = u.get_reset_password_token()
        new_u = User.verify_reset_password_token(token)
        new_token = token[0:] + (token[-1] + 1)
        new2_u = User.verify_reset_password_token(new_token)
        self.assertEqual(u, new_u)
        self.assertNotEqual(u, new2_u)

    def test_month_name(self):
        #u = User(username='brian')
        self.createTestUser()
        u = User.query.filter_by(username='brian').first()
        months = { 1:"January", 2:"February", 3:"March", 4:"April", 5:"May",
            6:"June", 7:"July", 8:"August", 9:"September", 10:"October",
            11:"November", 12:"December"}
        for num,name in months.items():
            self.assertEqual(name, u.month_name(num))

    def test_month_day(self):
        #u = User(username='brian')
        self.createTestUser()
        u = User.query.filter_by(username='brian').first()
        dates = u.month_days(2020, 2)
        day2_29 = date(2020, 2, 29)
        day3_1 = date(2020, 3, 1)
        self.assertTrue(day2_29 in dates)
        self.assertFalse(day3_1 in dates)

    def test_month_starting_balance(self):
        #u = User(username='brian')
        self.createTestUser()
        u = User.query.filter_by(username='brian').first()
        pass

if __name__ == '__main__':
        unittest.main(verbosity=2)
