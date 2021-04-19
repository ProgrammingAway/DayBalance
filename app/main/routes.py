from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.main.forms import TransactionForm
from app.models import User, Transaction
from app.main import bp


@bp.route("/", methods=["GET"])
@bp.route("/<int:year>/<int:month>", methods=["GET", "POST"])
@login_required
def index(year=0, month=0):
    """Show current balance calendar"""

    # set year and month to todays date if not supplied
    todays_date = datetime.date(datetime.now())
    if year == 0 or month == 0:
        year = todays_date.year
        month = todays_date.month

    month_name = current_user.month_name(month)
    weekday_headers = current_user.weekday_headers()
    start_balance = current_user.month_starting_balance(year, month)
    month_days = current_user.month_days(year, month)
    month_transactions = current_user.month_transactions(year, month)

    # render index.html with current variables
    return render_template(
        "index.html",
        todays_date=todays_date,
        current_month=month,
        current_year=year,
        current_months_name=month_name,
        weekday_headers=weekday_headers,
        month_days=month_days,
        balance=start_balance,
        transactions=month_transactions,
    )


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    form = TransactionForm(request.form)
    if request.method == 'POST' and form.validate():
        transaction = Transaction(
            user_id = current_user.id,
            title = form.title.data, 
            date = form.date.data,
            amount = form.amount.data,
            description = form.description.data,
            income = form.income.data,
            is_recurring = form.is_recurring.data,
            freq = form.freq.data,
            interval = form.interval.data,
            count = form.count.data,
            until = form.until.data,
        )
        if form.is_recurring.data:
            transaction.add_recurrence(form.byweekday.data)
        db.session.add(transaction)
        db.session.commit()

        flash("Transaction Added")
        return redirect(url_for("main.index"))
    return render_template(
        "transaction.html",
        title = "Add Transaction",
        form = form,
    )


@bp.route("/edit", methods=["GET", "POST"])
@bp.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    form = TransactionForm(request.form)
    edited_transaction = Transaction.query.filter_by(id=transaction_id).one()
    if request.method == 'POST' and form.validate():
        edited_transaction.title = form.title.data
        edited_transaction.date = form.date.data
        edited_transaction.amount = form.amount.data
        edited_transaction.description = form.description.data
        edited_transaction.income = form.income.data
        edited_transaction.is_recurring = form.is_recurring.data
        edited_transaction.freq = form.freq.data
        edited_transaction.interval = form.interval.data
        edited_transaction.count = form.count.data
        edited_transaction.until = form.until.data
        if form.is_recurring.data:
            edited_transaction.set_byweekday(form.byweekday.data)
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.index"))
    elif request.method == 'GET':
        form.title.data = edited_transaction.title
        form.date.data = edited_transaction.date
        form.amount.data = edited_transaction.amount
        form.description.data= edited_transaction.description
        form.income.data = edited_transaction.income
        form.is_recurring.data = edited_transaction.is_recurring
        form.freq.data = edited_transaction.freq
        form.interval.data = edited_transaction.interval
        form.count.data = edited_transaction.count
        form.until.data = edited_transaction.until
        if edited_transaction.is_recurring:
            form.byweekday.data = edited_transaction.return_byweekday()
    return render_template(
        "edit_transaction.html", 
        title = "Edit Transaction", 
        form = form, 
        transaction_id = edited_transaction.id,
    )


#@bp.route("/delete", methods=["GET"])
@bp.route("/delete/<int:transaction_id>", methods=["GET"])
@login_required
def delete_transaction(transaction_id):
    delete_transaction = Transaction.query.filter_by(id=transaction_id).one()
    db.session.delete(delete_transaction)
    db.session.commit()

    # Redirect user to home page
    flash("Transaction Deleted")
    return redirect(url_for("main.index"))
