from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, TransactionForm
from app.models import User, Transaction


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            title=form.title.data, 
            date=form.date.data,
            amount=form.amount.data,
            description=form.description.data,
            income=form.income.data,
        )
        db.session.add(transaction)
        db.session.commit()

        flash('Transaction Added')
        return redirect(url_for('index'))
    return render_template('transaction.html', title='Add Transaction', form=form)


@app.route("/edit", methods=["GET", "POST"])
@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    form = TransactionForm()
    edited_transaction = Transaction.query.filter_by(id=transaction_id).one()
    if form.validate_on_submit():
        edited_transaction.title = form.title.data
        edited_transaction.date = form.date.data
        edited_transaction.amount = form.amount.data
        edited_transaction.description = form.description.data
        edited_transaction.income = form.income.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.title.data = edited_transaction.title
        form.date.data = edited_transaction.date
        form.amount.data = edited_transaction.amount
        form.description.data= edited_transaction.description
        form.income.data = edited_transaction.income
    return render_template('edit_transaction.html', title='Edit Transaction', form=form, transaction_id=edited_transaction.id)


#@app.route("/delete", methods=["GET"])
@app.route("/delete/<int:transaction_id>", methods=["GET"])
@login_required
def delete_transaction(transaction_id):
    delete_transaction = Transaction.query.filter_by(id=transaction_id).one()
    db.session.delete(delete_transaction)
    db.session.commit()

    # Redirect user to home page
    flash('Transaction Deleted')
    return redirect(url_for('index'))


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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            start_date=form.start_date.data, 
            start_balance=form.start_balance.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        row = User.query.filter_by(username=form.username.data).first()

        transaction = Transaction(
            user_id=row.id,
            title="Initial Balance", 
            date=form.start_date.data,
            amount=form.start_balance.data,
            description="Initial Balance",
            income=True,
        )
        db.session.add(transaction)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
