import werkzeug.security
import jwt
import time
import flask
import flask_login
import calendar
import dateutil.rrule as rrule
import datetime
import app


@app.login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(flask_login.UserMixin, app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    username = app.db.Column(app.db.String(64), index=True, unique=True)
    email = app.db.Column(app.db.String(120), index=True, unique=True)
    password_hash = app.db.Column(app.db.String(128))
    start_date = app.db.Column(app.db.Date, nullable=False)
    start_balance = app.db.Column(app.db.Integer, nullable=False)
    transactions = app.db.relationship(
        'Transaction',
        backref='user',
        lazy='dynamic',
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_start_balance(self, start_balance):
        self.start_balance = int(round(start_balance * 100))

    def set_password(self, password):
        self.password_hash = werkzeug.security.generate_password_hash(password)

    def check_password(self, password):
        return werkzeug.security.check_password_hash(
            self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time.time() + expires_in},
            flask.current_app.config['SECRET_KEY'],
            algorithm='HS256')
#            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                flask.current_app.config['SECRET_KEY'],
                algorithms=['HS256'],
            )['reset_password']
        except Exception:
            return
        return User.query.get(id)

    def weekday_headers(self):
        weekday_headers = []
        for weekday in app.balance_calendar.iterweekdays():
            weekday_headers.append(calendar.day_abbr[weekday])
        return weekday_headers

    def month_name(self, month):
        return calendar.month_name[month]

    def month_days(self, year, month):
        return app.balance_calendar.itermonthdates(year, month)

    def return_transactions_between(self, before, after):
        """This function adds all transactions (recurring and non-recurring)
        that occurs for all dates between the budget start date and the
        first visible day of this calendar month.
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
            recurring_dates = (
                recurring_transaction.return_transactions_between(
                    before=before, after=after))
            transactions.extend(recurring_dates)

        return transactions

    def month_starting_balance(self, year, month):
        """Returns the starting balance for the current month.
        This function adds all transactions (recurring and non-recurring)
        that occurs for all dates between the budget start date and the
        first visible day of this calendar month.
        """
        month_start_day = list(
            app.balance_calendar.itermonthdates(year, month))[0]
        month_start_balance = 0

        prev_transactions = self.return_transactions_between(
            after=self.start_date,
            before=month_start_day,
        )

        for transaction in prev_transactions:
            if transaction.income is False:
                month_start_balance = month_start_balance - transaction.amount
            else:
                month_start_balance = month_start_balance + transaction.amount
        return (month_start_balance / 100)

    def month_transactions(self, year, month):
        """Returns all transactions (recurring and non-recurring) that
        occur durring all dates of the calendar that this month shows
        """
        month_start_day = list(
            app.balance_calendar.itermonthdates(year, month))[0]
        month_end_day = list(
            app.balance_calendar.itermonthdates(year, month))[-1]

        month_transactions = self.return_transactions_between(
            after=month_start_day,
            before=month_end_day,
        )

        return month_transactions


class Transaction(app.db.Model):
    # Inputs for database
    id = app.db.Column(app.db.Integer, primary_key=True)
    title = app.db.Column(app.db.String(40), nullable=False)
    date = app.db.Column(app.db.Date, nullable=False)
    amount = app.db.Column(app.db.Integer, nullable=False)
    description = app.db.Column(app.db.String(200))
    income = app.db.Column(app.db.Boolean)
    is_recurring = app.db.Column(app.db.Boolean)
    freq = app.db.Column(app.db.String(8))  # DAILY, WEEKLY, MONTHLY, YEARLY
    interval = app.db.Column(app.db.Integer)
    mon = app.db.Column(app.db.Boolean)
    tue = app.db.Column(app.db.Boolean)
    wed = app.db.Column(app.db.Boolean)
    thu = app.db.Column(app.db.Boolean)
    fri = app.db.Column(app.db.Boolean)
    sat = app.db.Column(app.db.Boolean)
    sun = app.db.Column(app.db.Boolean)
    # count and until cannot be used together
    count = app.db.Column(app.db.Integer)  # number of occurrences
    until = app.db.Column(app.db.Date)     # recurrence end date
    rrule_string = app.db.Column(app.db.String(100))
    user_id = app.db.Column(
        app.db.Integer,
        app.db.ForeignKey('user.id'),
        nullable=False,
    )

    # Other variables
    day_names = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    day_variables = [mon, tue, wed, thu, fri, sat, sun]
    freq_values = {
        'DAILY': rrule.DAILY,
        'WEEKLY': rrule.WEEKLY,
        'MONTHLY': rrule.MONTHLY,
        'YEARLY': rrule.YEARLY,
    }
    rrule_set = rrule.rruleset()

    def __repr__(self):
        return '<Transaction {}>'.format(self.title)

    def set_amount(self, amount):
        self.amount = int(round(amount * 100))

    def return_amount(self):
        return (self.amount / 100)

    def set_recurring(self, byweekday):
        byweekday_rrule = None
        for i in range(len(self.day_variables)):
            self.day_variables[i] = False
        if byweekday is not None and len(byweekday) > 0:
            byweekday_rrule = []
            for weekday in byweekday:
                self.day_variables[self.day_names.index(weekday)] = True
                byweekday_rrule.append(self.day_names.index(weekday))

        self.rrule_string = rrule.rrule(
            freq=self.freq_values[str(self.freq)],
            dtstart=self.date,
            interval=self.interval,
            count=self.count,
            until=self.until,
            byweekday=byweekday_rrule,
            wkst=app.balance_calendar.firstweekday,
        ).__str__()

        self.rrule_set = rrule.rruleset()
        self.rrule_set.rrule(rrule.rrulestr(self.rrule_string))

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
        before_datetime = datetime.datetime.combine(
            before, datetime.datetime.min.time())
        after_datetime = datetime.datetime.combine(
            after, datetime.datetime.min.time())

        # TZID error
        # recurring_dates = rrule.rrulestr(self.rrule_string).between(
        recurring_dates = self.rrule_set.between(
            before=before_datetime,
            after=after_datetime,
            inc=True,
        )

        recurring_transactions = []
        for date in recurring_dates:
            transaction = Transaction(
                id=self.id,
                user_id=self.user_id,
                title=self.title,
                date=date.date(),
                amount=self.amount,
                income=self.income,
            )
            recurring_transactions.append(transaction)

        return recurring_transactions
