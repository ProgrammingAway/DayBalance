from flask import current_app
import calendar
import datetime
import dateutil

class BalanceCalendar(calendar.Calendar):

    def __init__(self):
        if current_app.config['START_MONDAY']:
            self.firstweekday = 0  # 0 = Monday, 6 = Sunday
        else:
            self.firstweekday = 6

        super().__init__(self.firstweekday)




    # create weekday headers based on first weekday
    def weekday_headers():
        headers = []
        for weekday in self.iterweekdays():
            headers.append(calendar.day_abbr[weekday])
        return headers

    # set year and month to todays date if not supplied
    todays_date = datetime.date(datetime.now())
    if year == 0 or month == 0:
        year = todays_date.year
        month = todays_date.month

    # retrieve current month name and days for current month
    current_months_name = calendar.month_name[month]
    month_days = self.itermonthdates(year, month)

    month_day1 = list(self.itermonthdates(year, month))[0]
    prev_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= current_user.start_date, 
        Transaction.date < month_day1
    )
    # find transactions between current_user.start_date to 
    # month_days[0].day/month/year if any
    # for each transaction, add or subtract transaction from start_balance

    month_start_balance = 0
    for transaction in prev_transactions:
        if transaction.income == True:
            month_start_balance = month_start_balance + transaction.amount
        else:
            month_start_balance = month_start_balance - transaction.amount

