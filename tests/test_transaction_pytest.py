#!/usr/bin/env python
from app import create_app, db
from app.models import User, Transaction
from config import Config
from datetime import datetime, date
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY, SU, MO, TU, WE, TH, FR, SA
import pytest
from test_user_pytest import create_test_transaction


def test_amount(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t = create_test_transaction(user_id=user1.id)
    t.set_amount(123.45)
    assert 12345 == t.amount
    t.amount = 54321
    assert 543.21 == t.return_amount()

def test_set_recurring(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t = create_test_transaction(
        user_id=user1.id, 
        date=date(2021, 4, 1), 
        is_recurring=True, 
        freq="WEEKLY", 
        interval=1, 
        count=3,
    )
    t.set_recurring(["TH"])
    assert list(t.recurring_dates) == [datetime(2021, 4, 1), datetime(2021, 4, 8), datetime(2021, 4, 15)]
    assert ["TH"] == t.return_byweekday()
    t.set_recurring(["FR", "TU"])
    assert list(t.recurring_dates) == [datetime(2021, 4, 2), datetime(2021, 4, 6), datetime(2021, 4, 9)]
    assert ["TU", "FR"] == t.return_byweekday()
    t.set_recurring(None)
    assert list(t.recurring_dates) == [datetime(2021, 4, 1), datetime(2021, 4, 8), datetime(2021, 4, 15)]
    assert ["TH"] == t.return_byweekday()

def test_return_transactions_between(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t = create_test_transaction(
        user_id=user1.id, 
        date=date(2021, 4, 1), 
        is_recurring=True, 
        freq="WEEKLY", 
        interval=1, 
        count=3,
    )
    t.set_recurring(None)
    recurring_transactions = t.return_transactions_between(before=date(2021, 5, 1), after=date(2021, 4, 2))
    for transaction in recurring_transactions:
        assert transaction.title == t.title
        if transaction.date == date(2021, 4, 8) or transaction.date == date(2021, 4, 15):
            assert True
        else:
            assert transaction.date == date(2021, 4, 8)
