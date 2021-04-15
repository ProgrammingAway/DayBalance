from flask import current_app
from flask_login import current_user
import calendar
from app.models import Transaction

def current_months_name(month):
    return calendar.month_name[month]


class BalanceCalendar(calendar.Calendar):

    def __init__(self):
        if current_app.config['START_MONDAY']:
            self.firstweekday = 0  # 0 = Monday, 6 = Sunday
        else:
            self.firstweekday = 6

        super().__init__(self.firstweekday)
        
        # create weekday headers based on first weekday
        self.weekday_headers = []
        for weekday in self.iterweekdays():
            self.weekday_headers.append(calendar.day_abbr[weekday])

    def starting_balance(self, year, month):
        month_start_day = list(self.itermonthdates(year, month))[0]
        month_start_balance = 0

        prev_transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= current_user.start_date, 
            Transaction.date < month_start_day
        )

        for transaction in prev_transactions:
            if transaction.income == True:
                month_start_balance = month_start_balance + transaction.amount
            else:
                month_start_balance = month_start_balance - transaction.amount
        return month_start_balance

    def month_transactions(self, year, month):
        month_start_day = list(self.itermonthdates(year, month))[0]
        month_end_day = list(self.itermonthdates(year, month))[-1]
        return Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= month_start_day,
            Transaction.date <= month_end_day,
        )
