from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from calendar import day_abbr, month_name
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
    start_balance = db.Column(db.Float, nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
        return month_start_balance

    def month_transactions(self, year, month):
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_end_day = list(balance_calendar.itermonthdates(year, month))[-1]
        return Transaction.query.filter(
            Transaction.user_id == self.id,
            Transaction.date >= month_start_day,
            Transaction.date <= month_end_day,
        )


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    income = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Transaction {}>'.format(self.title)

# class RepeatedTransaction(Transaction):
#     freq = 1
#     interval = 1
#     wkst = None
#     count = None
#     until = None
#     bysetpos = None
#     bymonth = None
#     bymonthday = None
#     byyearday = None
#     byweekno = None
#     byweekday = None
#     cache = False
