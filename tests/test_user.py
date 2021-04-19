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
        t = Transaction(user_id=user_id, title=title, date=date, amount=amount, income=income, is_recurring=is_recurring)
        db.session.add(t)
        db.session.commit()
        return Transaction.query.filter_by(id=t.id).first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = self.createTestUser(username='panda', password='password')
        self.assertFalse(u.check_password('other_password'))
        self.assertTrue(u.check_password('password'))

    def test_token(self):
        u = self.createTestUser(username='panda')
        token_pass = u.get_reset_password_token()
        new_u_pass = User.verify_reset_password_token(token_pass)
        self.assertEqual(u, new_u_pass) # Test Passes
        # Move first character to the back to change the token
        token_fail = token_pass[1:] + token_pass[0]
        new_u_fail = User.verify_reset_password_token(token_fail)
        self.assertNotEqual(u, new_u_fail) # Test fails to no matching user
        u2 = self.createTestUser(username='oreo', password='password2', email='oreo@email.com')
        token_fail2 = u2.get_reset_password_token()
        new_u_fail2 = User.verify_reset_password_token(token_fail2)
        self.assertNotEqual(u, new_u_fail2) # Test fails to different user

    def test_month_name(self):
        u = self.createTestUser(username='panda')
        months = { 1:"January", 2:"February", 3:"March", 4:"April", 5:"May",
            6:"June", 7:"July", 8:"August", 9:"September", 10:"October",
            11:"November", 12:"December"}
        for num,name in months.items():
            self.assertEqual(name, u.month_name(num))

    def test_month_day(self):
        u = self.createTestUser(username='panda')
        dates = u.month_days(2020, 2)
        day2_29 = date(2020, 2, 29)
        day3_1 = date(2020, 3, 1)
        self.assertTrue(day2_29 in dates)
        self.assertFalse(day3_1 in dates)

    def test_month_starting_balance(self):
        u = self.createTestUser(username='panda', start_date=date(2021,1,1), start_balance=500.00)
        t1 = self.createTestTransaction(user_id=u.id, date=date(2021,6,5), amount='100', income=False)
        t2 = self.createTestTransaction(user_id=u.id, date=date(2021,6,12), amount='30.22', income=False)
        t3 = self.createTestTransaction(user_id=u.id, date=date(2021,6,22), amount='20', income=True)
        t4 = self.createTestTransaction(user_id=u.id, date=date(2021,7,4), amount='12.36', income=False)
        # 500-100-30.22+20=389.78 For June calendar
        july_start_balance = u.start_balance - float(u.month_starting_balance(2021, 7))
        self.assertEqual(389.78, july_start_balance)
        # 389.78-12.36=377.42 For July calendar
        august_start_balance = u.start_balance - float(u.month_starting_balance(2021, 8))
        self.assertEqual(377.42, august_start_balance)

    def test_month_transactions(self):
        u = self.createTestUser(username='panda')
        pass

if __name__ == '__main__':
        unittest.main(verbosity=2)
