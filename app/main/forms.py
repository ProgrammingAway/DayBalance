from wtforms import Form, DecimalField, SubmitField, TextAreaField
from wtforms import StringField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange, Optional
from wtforms.fields.html5 import DateField
from app.models import User
from flask_login import current_user

class TransactionForm(Form):
    title = StringField('Transaction Name', validators=[InputRequired()])
    date = DateField('Transaction Date', validators=[InputRequired()])
    amount = DecimalField('Transaction Amount', validators=[InputRequired()], places=2)
    description = TextAreaField('Description', validators=[Length(min=0, max=140)])
    income = BooleanField('Income')
    is_recurring = BooleanField('Recurring')
    freq = SelectField('Frequency', choices=[('YEARLY', 'Year(s)'), ('MONTHLY', 'Month(s)'), ('WEEKLY', 'Week(s)'), ('DAILY', 'Day(s)')], validators=[Optional()])
    interval = DecimalField('Frequency Interval', validators=[NumberRange(min=1, max=100), Optional()], places=0)
    byweekday = SelectMultipleField('Day of the Week', choices=[('sun', 'Sunday'), ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday')], validators=[Optional()])
    # Cannot use until and count together
    count = DecimalField('Number of Transactions', validators=[NumberRange(min=1, max=100), Optional()], places=0)
    until = DateField('End Date', validators=[Optional()])
    submit = SubmitField('Submit')

    def validate_date(self, date):
        start_date = current_user.start_date
        if date.data < start_date:
            raise ValidationError(
                'Please use a date after the budget start date: '
                + str(start_date) + '.'
            )

    def validate_until(self, until):
        if until.data is not None:
            if self.count.data is not None:
                raise ValidationError("Select 'End Date' or 'Number of Transactions', but not both.")
            if until.data < self.date.data:
                raise ValidationError('Please use an end date after the transaction date.')
