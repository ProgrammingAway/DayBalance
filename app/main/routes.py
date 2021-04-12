from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.main.forms import TransactionForm
from app.models import User, Transaction
from app.main import bp
import calendar


@bp.route("/", methods=["GET"])
@bp.route("/<int:year>/<int:month>", methods=["GET", "POST"])
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

    month_day1 = list(current_calendar.itermonthdates(year, month))[0]
    prev_transactions = Transaction.query.filter(Transaction.user_id == current_user.id,
        Transaction.date >= current_user.start_date, Transaction.date < month_day1)
    # find transactions between current_user.start_date to month_days[0].day/month/year if any
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
        transactions=current_user.transactions,
    )


@bp.route("/add", methods=["GET", "POST"])
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
        return redirect(url_for('main.index'))
    return render_template('transaction.html', title='Add Transaction', form=form)


@bp.route("/edit", methods=["GET", "POST"])
@bp.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
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


#@bp.route("/delete", methods=["GET"])
@bp.route("/delete/<int:transaction_id>", methods=["GET"])
@login_required
def delete_transaction(transaction_id):
    delete_transaction = Transaction.query.filter_by(id=transaction_id).one()
    db.session.delete(delete_transaction)
    db.session.commit()

    # Redirect user to home page
    flash('Transaction Deleted')
    return redirect(url_for('main.index'))
