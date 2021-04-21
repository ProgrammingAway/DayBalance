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

# def test_set_recurring(db_one_user):
#     db_one_user
#     user1 = User.query.filter_by(username='Panda').first()
#     t = create_test_transaction(user_id=user1.id, date=date(2021, 4, 1), is_recurring=True, freq=WEEKLY)
#     t.set_recurring()
#     assert t.recurring_dates is False

# def test_byweekday(db_one_user):
#     db_one_user
#     user1 = User.query.filter_by(username='Panda').first()
#     t = createTestTransaction(user_id=user1.id)
#     t.set_byweekday(["sun"])
#     assert True == t.day["sun"]
#     assert False == t.day["mon"]
#     t.day = {"mon":True, "sun":False}
#     byweekday = t.return_byweekday()
#     assert "mon" in byweekday
#     assert "sun" not in byweekday
#     assert "wed" not in byweekday
