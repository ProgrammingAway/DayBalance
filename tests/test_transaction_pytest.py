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
    t1 = create_test_transaction(
        user_id=user1.id, 
        date=date(2021, 4, 1), 
        is_recurring=True, 
        freq="WEEKLY", 
        interval=1, 
        count=3,
    )
    recurring_transactions1 = t1.return_transactions_between(before=date(2021, 5, 1), after=date(2021, 4, 2))
    assert t1.freq == 'WEEKLY'
    assert t1.freq_values[str(t1.freq)] == WEEKLY
    for transaction in recurring_transactions1:
        assert transaction.title == t1.title
        if transaction.date in [ date(2021, 4, 8), date(2021, 4, 15) ]:
            assert True
        else:
            assert transaction.date == False

    t2 = create_test_transaction(
        user_id=user1.id,
        title="Another Recurring Bill",
        date=date(2021, 5, 5), 
        is_recurring=True, 
        freq="MONTHLY", 
        interval=1, 
    )
    recurring_transactions2 = t2.return_transactions_between(before=date(2021, 8, 1), after=date(2021, 5, 1))
    assert t2.freq == 'MONTHLY'
    assert t2.freq_values[str(t2.freq)] == MONTHLY
    for transaction in recurring_transactions2:
        assert transaction.title == t2.title
        if transaction.date in [ date(2021, 5, 5), date(2021, 6, 5), date(2021, 7, 5) ]:
            assert True
        else:
            assert transaction.date == False
