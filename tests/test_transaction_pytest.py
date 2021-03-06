#!/usr/bin/env python
from app import create_app, db
from app.models import User, Transaction
from app.main.forms import TransactionForm
from config import Config
from datetime import datetime, date
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY, SU, MO, TU, WE, TH, FR, SA
import pytest
from test_user_pytest import create_test_transaction, create_test_exception


def test_form_validate(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    user1.start_date = date(2021, 3, 1)
    #transaction1_form = TransactionForm(title="Bill1", date=date(2021, 2, 1), amount=100.00)
    #assert transaction1_form.validate() == False
    #transaction2_form = TransactionForm(title="Bill2", date=date(2021, 3, 1), amount=200.00)
    #assert transaction2_form.validate() == True
    #transaction3_form = TransactionForm(title="Bill3", date=date(2021, 4, 1), amount=300.00, until=date(2021, 10, 1))
    #assert transaction3_form.validate() == True
    #transaction4_form = TransactionForm(title="Bill4", date=date(2021, 5, 1), amount=400.00, until=date(2021, 2, 15))
    #assert transaction4_form.validate() == False
    #transaction5_form = TransactionForm(title="Bill5", date=date(2021, 6, 1), amount=500.00, until=date(2021, 10, 1), count=3)
    #assert transaction5_form.validate() == False
    #transaction6_form = TransactionForm(title="Bill6", date=date(2021, 7, 1), amount=600.00, count=3)
    #assert transaction6_form.validate() == True
    pass

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
    assert ["TH"] == t.return_byweekday()
    assert t.rrule_string == 'DTSTART:20210401T000000\nRRULE:FREQ=WEEKLY;COUNT=3;BYDAY=TH'
    t.set_recurring(["FR", "TU"])
    assert ["TU", "FR"] == t.return_byweekday()
    assert t.rrule_string == 'DTSTART:20210401T000000\nRRULE:FREQ=WEEKLY;COUNT=3;BYDAY=TU,FR'
    t.set_recurring(None)
    assert [] == t.return_byweekday()
    assert t.rrule_string == 'DTSTART:20210401T000000\nRRULE:FREQ=WEEKLY;COUNT=3'

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
    for transaction in recurring_transactions1:
        assert transaction.title == t1.title
        if transaction.date in [ date(2021, 4, 8), date(2021, 4, 15) ]:
            assert True
        else:
            assert transaction.date == False

    e1 = create_test_exception(
        user_id=user1.id, 
        transaction_id=t1.id,
        date=date(2021, 4, 8), 
        delete=True, 
    )
    recurring_transactions2 = t1.return_transactions_between(before=date(2021, 5, 1), after=date(2021, 4, 1))
    for transaction in recurring_transactions2:
        assert transaction.title == t1.title
        if transaction.date in [ date(2021, 4, 1), date(2021, 4, 15) ]:
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
    recurring_transactions3 = t2.return_transactions_between(before=date(2021, 8, 1), after=date(2021, 5, 1))
    for transaction in recurring_transactions3:
        assert transaction.title == t2.title
        if transaction.date in [ date(2021, 5, 5), date(2021, 6, 5), date(2021, 7, 5) ]:
            assert True
        else:
            assert transaction.date == False

    e2 = create_test_exception(
        user_id=user1.id, 
        transaction_id=t2.id,
        date=date(2021, 6, 5), 
        delete=True, 
    )
    e3 = create_test_exception(
        user_id=user1.id, 
        transaction_id=t2.id,
        date=date(2021, 5, 28), 
        delete=False, 
    )
    recurring_transactions4 = t2.return_transactions_between(before=date(2021, 8, 1), after=date(2021, 5, 1))
    for transaction in recurring_transactions4:
        assert transaction.title == t2.title
        if transaction.date in [ date(2021, 5, 5), date(2021, 5, 28), date(2021, 7, 5) ]:
            assert True
        else:
            assert transaction.date == False
