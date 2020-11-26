import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import calendar
from datetime import date, datetime, timedelta

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
#app.config["TEMPLATES_AUTO_RELOAD"] = True

# set up database using SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daybalance.db'
app.config['SECRET_KEY'] = "lkjhoiuehbakj"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(120), unique=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    start_balance = db.Column(db.Float, nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    account = db.Column(db.String(40))
    category = db.Column(db.String(40))
    cleared = db.Column(db.Boolean)
    income = db.Column(db.Boolean)
    repeat = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

db.create_all()

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/add", methods=["GET", "POST"])
@login_required
#def add_transaction(year, month, day):
def add_transaction():
    """ add one month from given month and year """
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            return apology("must provide transaction title", 403)

        # Ensure date was submitted
        elif not request.form.get("date"):
            return apology("must provide transaction date", 403)

        # Ensure amount was submitted
        elif not request.form.get("amount"):
            return apology("must provide transaction amount", 403)

        year, month, day = map(int, request.form.get("date").split('-'))

        # Create new transaction
        new_transaction = Transaction(
            user_id=session["user_id"],
            title=request.form.get("title"), 
            date=datetime(year, month, day),
            amount=request.form.get("amount"),
            account=(request.form.get("account") if request.form.get("account") else ""),
            category=(request.form.get("category") if request.form.get("category") else ""),
            description=(request.form.get("description") if request.form.get("description") else ""),
            cleared=(True if request.form.get("cleared") == "Cleared" else False),
            income=(True if request.form.get("income") == "Income" else False),
            repeat=(True if request.form.get("repeat") == "Repeat" else False),
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Redirect user to home page
        flash('Transaction Added')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("transaction.html")


@app.route("/", methods=["GET", "POST"])
@app.route("/<int:year>/<int:month>", methods=["GET", "POST"])
@login_required
def index(year=0, month=0):
    """Show current balance calendar"""

    first_weekday = 6 # 0 = Monday, 6 = Sunday

    # create calendar based on first weekday
    current_calendar = calendar.Calendar(first_weekday)

    # create weekday headers based on first weekday
    weekdays_headers = []
    for weekday in current_calendar.iterweekdays():
        weekdays_headers.append(calendar.day_abbr[weekday])

    # set year and month to todays date if not supplied
    todays_date = datetime.date(datetime.now())
    if year == 0 or month == 0:
        year = todays_date.year
        month = todays_date.month

    # retrieve current month name and days for current month
    current_months_name = calendar.month_name[month]
    month_days = current_calendar.itermonthdates(year, month)
    user = User.query.filter_by(id=session["user_id"]).first()

#    prev_transactions = Transaction.query.filter(
#        and_(Transaction.id == session["user_id"],
#        Transaction.date >= user.start_date, Transaction.date < month_days.next())
#    )
    # find transactions between user.start_date to month_days[0].day/month/year if any
    # for each transaction, add or subtract transaction from start_balance 

    # render index.html with current variables
    return render_template("index.html",
        todays_date=todays_date,
        current_month=month,
        current_year=year,
        current_months_name=current_months_name,
        weekdays_headers=weekdays_headers,
        month_days=month_days,
        balance=1010,
        transactions=user.transactions,
    )


@app.route("/graph", methods=["GET", "POST"])
@login_required
def graph():
    """Graph daily balance."""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/settings")
@login_required
def settings():
    """Show app settings"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        row = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if row is None or not check_password_hash(row.hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row.id

        # Redirect user to home page
        flash('You were successfully logged in')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        # Ensure password was submitted
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password does not match confirmation", 403)

        # Ensure start date was submitted
        elif not request.form.get("start_date"):
            return apology("must provide budget start date", 403)

        # Ensure password was submitted
        elif not request.form.get("start_balance"):
            return apology("must provide budget start balance", 403)

        # TODO: Check password rules!

        year, month, day = map(int, request.form.get("start_date").split('-'))

        # Query database for username
        new_user = User(username=request.form.get("username"), 
            hash=generate_password_hash(request.form.get("password")),
            start_date=datetime(year, month, day),
            start_balance=request.form.get("start_balance"))
        db.session.add(new_user)
        db.session.commit()

        row = User.query.filter_by(username=request.form.get("username")).first()

        # Create new transaction
        new_transaction = Transaction(
            user_id=row.id,
            title="Initial Balance", 
            date=datetime(year, month, day),
            amount=request.form.get("start_balance"),
            account="",
            category="",
            description="",
            cleared=True,
            income=True,
            repeat=False,
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Redirect user to home page
        flash('Registration successful')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
