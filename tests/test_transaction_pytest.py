#!/usr/bin/env python
from app import create_app, db
from app.models import User, Transaction
from config import Config
from datetime import datetime, date
import pytest


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
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t = createTestTransaction(user_id=user1.id)
    t.set_amount(123.45)
    assert 12345 == t.amount
    t.amount = 54321
    assert 543.21 == t.return_amount()

def test_byweekday(db_one_user):
    db_one_user
    user1 = User.query.filter_by(username='Panda').first()
    t = createTestTransaction(user_id=user1.id)
    t.set_byweekday(["sun"])
    assert True == t.day["sun"]
    assert False == t.day["mon"]
    t.day = {"mon":True, "sun":False}
    byweekday = t.return_byweekday()
    assert "mon" in byweekday
    assert "sun" not in byweekday
    assert "wed" not in byweekday
    
