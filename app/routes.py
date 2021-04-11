#import os

#from flask import Flask, flash, jsonify, redirect, render_template, request, session
#from flask_session import Session
#from flask_sqlalchemy import SQLAlchemy
#from tempfile import mkdtemp
#from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
#from werkzeug.security import check_password_hash, generate_password_hash
#import calendar

#from datetime import date, datetime, timedelta

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    """ add transaction """
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

        user = User.query.filter_by(id=session["user_id"]).first()
        user.transactions.append(new_transaction)
        #db.session.add(new_transaction)
        db.session.commit()

        # Redirect user to home page
        flash('Transaction Added')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("transaction.html")


@app.route("/edit", methods=["GET", "POST"])
@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    """ edit transaction """

    edited_transaction = Transaction.query.filter_by(id=transaction_id).one()

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

        # Edit transaction
        edited_transaction.title=request.form.get("title")
        edited_transaction.date=datetime(year, month, day)
        edited_transaction.amount=request.form.get("amount")
        edited_transaction.account=(request.form.get("account") if request.form.get("account") else "")
        edited_transaction.category=(request.form.get("category") if request.form.get("category") else "")
        edited_transaction.description=(request.form.get("description") if request.form.get("description") else "")
        edited_transaction.cleared=(True if request.form.get("cleared") == "Cleared" else False)
        edited_transaction.income=(True if request.form.get("income") == "Income" else False)
        edited_transaction.repeat=(True if request.form.get("repeat") == "Repeat" else False)

        db.session.commit()

        # Redirect user to home page
        flash('Transaction Modified')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        date = str(edited_transaction.date.year) + "-" + str(edited_transaction.date.month) + "-" + str(edited_transaction.date.day)
        return render_template("edit_transaction.html", 
            transaction=edited_transaction,
            date=date,
        )


#@app.route("/delete", methods=["GET"])
@app.route("/delete/<int:transaction_id>", methods=["GET"])
@login_required
def delete_transaction(transaction_id):
    """ delete transaction """

    delete_transaction = Transaction.query.filter_by(id=transaction_id).one()
    db.session.delete(delete_transaction)
    db.session.commit()

    # Redirect user to home page
    flash('Transaction Deleted')
    return redirect("/")


@app.route("/", methods=["GET"])
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

    month_day1 = list(current_calendar.itermonthdates(year, month))[0]
    prev_transactions = Transaction.query.filter(Transaction.user_id == session["user_id"],
        Transaction.date >= user.start_date, Transaction.date < month_day1)
    # find transactions between user.start_date to month_days[0].day/month/year if any
    # for each transaction, add or subtract transaction from start_balance 

    month_start_balance = 0
    for transaction in prev_transactions:
        if transaction.income == True:
            month_start_balance = month_start_balance + transaction.amount
        else:
            month_start_balance = month_start_balance - transaction.amount

    # render index.html with current variables
    return render_template("index.html",
        todays_date=todays_date,
        current_month=month,
        current_year=year,
        current_months_name=current_months_name,
        weekdays_headers=weekdays_headers,
        month_days=month_days,
        balance=month_start_balance,
        transactions=user.transactions,
    )

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
