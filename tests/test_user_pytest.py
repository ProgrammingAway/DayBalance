#!/usr/bin/env python
from app import db
from app.models import User, Transaction
from datetime import datetime, date
import pytest

def create_test_transaction(
    user_id,
    title='Test Transaction',
    date=datetime.now(),
    amount=100.00,
    description='Test Description',
    income=False,
    is_recurring=False,
    freq=None,
    interval=None,
    count=None,
    until=None,
):
    t = Transaction(
        user_id=user_id,
        title=title,
        date=date,
        income=income,
        is_recurring=is_recurring,
        freq=freq,
        interval=interval,
        count=count,
        until=until,
    )
    t.set_amount(amount)
    if is_recurring:
        t.set_recurring(None)
    db.session.add(t)
    db.session.commit()
    return Transaction.query.filter_by(id=t.id).first()

def test_password_hashing(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    assert user1.check_password('other_password') is False
    assert user1.check_password('password') is True

def test_token(db_two_users):
    db_two_users
    user1 = User.query.filter_by(username='Panda').first()
    token_pass = user1.get_reset_password_token()
    return1_user = User.verify_reset_password_token(token_pass)
    assert user1 == return1_user
    # Move first character to the back to change the token
    token_fail = token_pass[1:] + token_pass[0]
    return2_user = User.verify_reset_password_token(token_fail)
    assert user1 != return2_user
    user2 = User.query.filter_by(username='Oreo').first()
    token_fail2 = user2.get_reset_password_token()
    return3_user = User.verify_reset_password_token(token_fail2)
    assert user1 != return3_user

def test_set_start_balance(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    assert 123456 == user1.start_balance

def test_weekday_headers_mon(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    assert weekdays == user1.weekday_headers()

def test_weekday_headers_sun(db_one_user_sun):
    db_one_user_sun
    user1 = User.query.filter_by(username='Panda').first()
    weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    assert weekdays == user1.weekday_headers()

def test_month_name(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    months = { 1:"January", 2:"February", 3:"March", 4:"April", 5:"May",
        6:"June", 7:"July", 8:"August", 9:"September", 10:"October",
        11:"November", 12:"December"}
    for num,name in months.items():
        assert name ==  user1.month_name(num)

def test_month_day(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    dates = user1.month_days(2020, 2)
    day2_29 = date(2020, 2, 29)
    day3_15 = date(2020, 3, 15)
    assert day2_29 in dates
    assert day3_15 not in dates

def test_month_starting_balance(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t1 = create_test_transaction(user_id=user1.id, date=date(2021,6,5), amount=100.00, income=False)
    t2 = create_test_transaction(user_id=user1.id, date=date(2021,6,12), amount=30.22, income=False)
    t3 = create_test_transaction(user_id=user1.id, date=date(2021,6,22), amount=20.00, income=True)
    t4 = create_test_transaction(user_id=user1.id, date=date(2021,7,4), amount=12.36, income=False)
    t5 = create_test_transaction(
        user_id=user1.id, 
        date=date(2021,2,6), 
        amount=2.22,
        income=False,
        is_recurring=True, 
        freq="MONTHLY", 
        interval=1, 
    )

    july_start_balance = 0 - (5 * t5.amount) # recurring transactions
    for transaction in [t1, t2, t3]:
        if transaction.income:
            july_start_balance = july_start_balance + transaction.amount
        else:
            july_start_balance = july_start_balance - transaction.amount
    # result = 0 - 110.22 - 11.10 (recurr) = -121.32
    assert (july_start_balance / 100) == user1.month_starting_balance(2021, 7)

    august_start_balance = july_start_balance - t5.amount
    for transaction in [t4]:
        if transaction.income:
            august_start_balance = august_start_balance + transaction.amount
        else:
            august_start_balance = august_start_balance - transaction.amount
    # result = -121.32 - 12.36 - 2.22 (recurr) = -135.90
    assert (august_start_balance / 100) == user1.month_starting_balance(2021, 8)

def test_month_transactions(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t1 = create_test_transaction(user_id=user1.id, date=date(2021,6,5), amount=100.00, income=False)
    t2 = create_test_transaction(user_id=user1.id, date=date(2021,6,12), amount=30.22, income=False)
    t3 = create_test_transaction(user_id=user1.id, date=date(2021,6,22), amount=20.00, income=True)
    t4 = create_test_transaction(user_id=user1.id, date=date(2021,7,4), amount=12.36, income=False)
    t5 = create_test_transaction(
        user_id=user1.id, 
        date=date(2021,2,6), 
        amount=2.22,
        income=False,
        is_recurring=True, 
        freq="MONTHLY", 
        interval=1, 
    )

    month_transactions = user1.month_transactions(2021, 6)
    assert len(month_transactions) == 4
    for transaction in month_transactions:
        if transaction.date in [ date(2021, 6, 5), date(2021, 6, 12), date(2021, 6, 22), date(2021, 6, 6) ]:
            assert True
        else:
            assert transaction.date == False

    month_transactions = user1.month_transactions(2021, 7)
    assert len(month_transactions) == 2
    for transaction in month_transactions:
        if transaction.date in [ date(2021, 7, 4), date(2021, 7, 6) ]:
            assert True
        else:
            assert transaction.date == False

