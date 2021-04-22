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

    def return_transactions_between(self, before, after):
        """This function adds all transactions (recurring and non-recurring) that
        occurs for all dates between the budget start date and the first
        visible day of this calendar month.
        """
        transactions = Transaction.query.filter(
            Transaction.user_id == self.id,
            Transaction.is_recurring == False,
            Transaction.date >= after,
            Transaction.date < before,
        ).all()

        recurring_transactions = Transaction.query.filter(
            Transaction.user_id == self.id,
            Transaction.is_recurring == True,
        )

        for recurring_transaction in recurring_transactions:
            recurring_dates = recurring_transaction.return_transactions_between(before=before, after=after)
            transactions.extend(recurring_dates)

        return transactions


    def month_starting_balance(self, year, month):
        """Returns the starting balance for the current month.
        This function adds all transactions (recurring and non-recurring) that
        occurs for all dates between the budget start date and the first
        visible day of this calendar month.
        """
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_start_balance = 0

        prev_transactions = self.return_transactions_between(after=self.start_date, before=month_start_day)

        for transaction in prev_transactions:
            if transaction.income == True:
                month_start_balance = month_start_balance + transaction.amount
            else:
                month_start_balance = month_start_balance - transaction.amount
        return (month_start_balance / 100)

    def month_transactions(self, year, month):
        """Returns all transactions (recurring and non-recurring) that
        occur durring all dates of the calendar that this month shows
        """
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_end_day = list(balance_calendar.itermonthdates(year, month))[-1]

        month_transactions = self.return_transactions_between(after=month_start_day, before=month_end_day)

        return month_transactions


class Transaction(db.Model):
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
    mon = db.Column(db.Boolean)
    tue = db.Column(db.Boolean)
    wed = db.Column(db.Boolean)
    thu = db.Column(db.Boolean)
    fri = db.Column(db.Boolean)
    sat = db.Column(db.Boolean)
    sun = db.Column(db.Boolean)
    count = db.Column(db.Integer)  # number of occurrences (Cannot be used with until)
    until = db.Column(db.Date)     # recurrence end date (Cannot be used with count)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Other variables
    day_names = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    day_variables = [ mon, tue, wed, thu, fri, sat, sun ]
    freq_values =  {'DAILY':DAILY, 'WEEKLY':WEEKLY, 'MONTHLY':MONTHLY, 'YEARLY':YEARLY}
    recurring_dates = rruleset()

    def __repr__(self):
        return '<Transaction {}>'.format(self.title)

    def set_amount(self, amount):
        self.amount = int(round(amount * 100))

    def return_amount(self):
        return (self.amount / 100)

    def set_recurring(self, byweekday):
        byweekday_rrule = []
        for i in range(len(self.day_variables)):
            self.day_variables[i] = False
        if byweekday is None or len(byweekday) == 0:
            weekday_num = self.date.weekday()
            byweekday_rrule = None
            self.day_variables[weekday_num] = True
        else:
            for weekday in byweekday:
                self.day_variables[self.day_names.index(weekday)] = True
                byweekday_rrule.append(self.day_names.index(weekday))

        freq_rrule = self.freq_values[str(self.freq)]
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

    def return_byweekday(self):
        byweekday = []
        for i in range(len(self.day_variables)):
            if self.day_variables[i] is True:
                byweekday.append(self.day_names[i])
        return byweekday

    def return_transactions_between(self, before, after):
        """Returns all recurring transactions that
        occur between the start and end date
        """
        before_datetime = datetime.combine(before, datetime.min.time())
        after_datetime = datetime.combine(after, datetime.min.time())

        recurring_transactions = []
        recurring_dates = self.recurring_dates.between(before=before_datetime, after=after_datetime, inc=True)
        for date in recurring_dates:
            transaction = Transaction(
                id = self.id,
                user_id = self.user_id,
                title = self.title, 
                date = date.date(),
                amount = self.amount,
                income = self.income,
            )
            recurring_transactions.append(transaction)

        return recurring_transactions
