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

    def createTestUser(
        self,
        username='name',
        password='password',
        email='name@email.com',
        start_date=datetime.now(),
        start_balance=10.00,
    ):
        u = User(username=username)
        u.set_password(password)
        u.email = email
        u.start_date = start_date
        u.start_balance = start_balance
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        self.createTestUser(username='panda', password='password')
        u = User.query.filter_by(username='panda').first()
        self.assertFalse(u.check_password('other_password'))
        self.assertTrue(u.check_password('password'))

    def test_token(self):
        self.createTestUser(username='panda')
        u = User.query.filter_by(username='panda').first()
        token_pass = u.get_reset_password_token()
        new_u_pass = User.verify_reset_password_token(token_pass)
        self.assertEqual(u, new_u_pass)
        # Move first character to the back to change the token
        token_fail = token_pass[1:] + token_pass[0]
        new_u_fail = User.verify_reset_password_token(token_fail)
        self.assertNotEqual(u, new_u_fail)
        self.createTestUser(username='oreo', password='password2', email='oreo@email.com')
        u2 = User.query.filter_by(username='oreo').first()
        token_fail2 = u2.get_reset_password_token()
        new_u_fail2 = User.verify_reset_password_token(token_fail2)
        self.assertNotEqual(u, new_u_fail2)

    def test_month_name(self):
        self.createTestUser(username='panda')
        u = User.query.filter_by(username='panda').first()
        months = { 1:"January", 2:"February", 3:"March", 4:"April", 5:"May",
            6:"June", 7:"July", 8:"August", 9:"September", 10:"October",
            11:"November", 12:"December"}
        for num,name in months.items():
            self.assertEqual(name, u.month_name(num))

    def test_month_day(self):
        self.createTestUser(username='panda')
        u = User.query.filter_by(username='panda').first()
        dates = u.month_days(2020, 2)
        day2_29 = date(2020, 2, 29)
        day3_1 = date(2020, 3, 1)
        self.assertTrue(day2_29 in dates)
        self.assertFalse(day3_1 in dates)

    def test_month_starting_balance(self):
        self.createTestUser(username='panda')
        u = User.query.filter_by(username='panda').first()
        pass

if __name__ == '__main__':
        unittest.main(verbosity=2)
