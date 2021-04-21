from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin
from calendar import day_abbr, month_name
from time import time
from datetime import datetime
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from dateutil.rrule import rrule, rruleset, SU, MO, TU, WE, TH, FR, SA
import jwt
from app import db, login, balance_calendar


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    start_date = db.Column(db.Date, nullable=False)
    start_balance = db.Column(db.Integer, nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_start_balance(self, start_balance):
        self.start_balance = int(round(start_balance * 100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256')
#            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def weekday_headers(self):
        weekday_headers = []
        for weekday in balance_calendar.iterweekdays():
            weekday_headers.append(day_abbr[weekday])
        return weekday_headers

    def month_name(self, month):
        return month_name[month]

    def month_days(self, year, month):
        return balance_calendar.itermonthdates(year, month)

    def month_starting_balance(self, year, month):
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_start_balance = 0

        prev_transactions = Transaction.query.filter(
            Transaction.user_id == self.id,
            Transaction.date >= self.start_date,
            Transaction.date < month_start_day
        )

        for transaction in prev_transactions:
            if transaction.income == True:
                month_start_balance = month_start_balance + transaction.amount
            else:
                month_start_balance = month_start_balance - transaction.amount
        return (month_start_balance / 100)

    def month_transactions(self, year, month):
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_end_day = list(balance_calendar.itermonthdates(year, month))[-1]
        month_transactions = Transaction.query.filter(
            Transaction.user_id == self.id,
#            Transaction.is_recurring == False,
            Transaction.date >= month_start_day,
            Transaction.date <= month_end_day,
        )

        #recurring_transactions = Transaction.query.filter(
        #    Transaction.user_id == self.id,
        #    Transaction.is_recurring == True,
        #)

        #recurring = []
        #for transaction in recurring_transactions:
        #    recurring.append(transaction.return_transactions_between(month_start_day, month_end_day))

        return month_transactions


class Transaction(db.Model):
    day_values = {'SU':SU, 'MO':MO, 'TU':TU, 'WE':WE, 'TH':TH, 'FR':FR, 'SA':SA}
    freq_values =  {'DAILY':DAILY, 'WEEKLY':WEEKLY, 'MONTHLY':MONTHLY, 'YEARLY':YEARLY}
    recurring_dates = rruleset()

    # Inputs for database
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    income = db.Column(db.Boolean)
    is_recurring = db.Column(db.Boolean)
    freq = db.Column(db.String(8))  # DAILY, WEEKLY, MONTHLY, YEARLY
    interval = db.Column(db.Integer)
    day = {}
    day['MO'] = db.Column(db.Boolean)
    day['TU'] = db.Column(db.Boolean)
    day['WE'] = db.Column(db.Boolean)
    day['TH'] = db.Column(db.Boolean)
    day['FR'] = db.Column(db.Boolean)
    day['SA'] = db.Column(db.Boolean)
    day['SU'] = db.Column(db.Boolean)
    count = db.Column(db.Integer)  # number of occurrences (Cannot be used with until)
    until = db.Column(db.Date)     # recurrence end date (Cannot be used with count)
    transaction_exceptions = db.relationship('TransactionException', backref='transaction', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Transaction {}>'.format(self.title)

    def set_amount(self, amount):
        self.amount = int(round(amount * 100))

    def return_amount(self):
        return (self.amount / 100)

    def return_byweekday(self):
        byweekday = []
        for key,value in self.day.items():
            if value is True:
                byweekday.append(key)
        return byweekday

    def set_recurring(self, byweekday=[]):
        byweekday_rrule = []
        for key in self.day.keys():
            self.day[key] = False
        if byweekday is not None:
            for weekday in byweekday:
                self.day[weekday] = True
                byweekday_rrule.append(self.day_values[weekday])
        freq_rrule = self.freq_values[self.freq]
        self.recurring_dates = rruleset()
        self.recurring_dates.rrule(rrule(
            freq=freq_rrule,
            dtstart=self.date,
            interval=self.interval,
            count=self.count,
            until=self.until,
            byweekday=byweekday_rrule,
            wkst=balance_calendar.firstweekday,
        ))

    def return_transactions_between(self, start, end):
        #for exception in exceptions:
        #    if exception.delete:
        #        self.recurring_dates.exdate(exception.date)
        #    else:
        #        self.recurring_dates.rdate(exception.date)

        start_datetime = datetime.combine(start, datetime.min.time())
        end_datetime = datetime.combine(end, datetime.min.time())
        return self.recurring_dates.between(before=start_datetime, after=end_datetime, inc=True)

class TransactionException(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    delete = db.Column(db.Boolean)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
