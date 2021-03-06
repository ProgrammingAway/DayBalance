from wtforms import Form, DecimalField, IntegerField, SubmitField
from wtforms import TextAreaField, StringField, BooleanField
from wtforms import SelectField, SelectMultipleField, RadioField
from wtforms.validators import InputRequired, Length, ValidationError
from wtforms.validators import NumberRange, Optional
from wtforms.fields.html5 import DateField
from app.models import User
from flask_login import current_user


class TransactionForm(Form):
    title = StringField('Transaction Name', validators=[InputRequired()])
    date = DateField('Transaction Date', validators=[InputRequired()])
    amount = DecimalField(
        'Transaction Amount',
        validators=[InputRequired()],
        places=2,
    )
    description = TextAreaField(
        'Description',
        validators=[Length(min=0, max=140)],
    )
    income = BooleanField('Income')
    is_recurring = BooleanField('Recurring')
    freq = SelectField(
        'Frequency',
        choices=[
            ('YEARLY', 'Year(s)'),
            ('MONTHLY', 'Month(s)'),
            ('WEEKLY', 'Week(s)'),
            ('DAILY', 'Day(s)'),
        ],
        validators=[Optional()],
        default='MONTHLY',
    )
    interval = IntegerField(
        'Frequency Interval',
        validators=[NumberRange(min=1, max=100), Optional()],
    )
    byweekday = SelectMultipleField(
        'Day of the Week',
        choices=[
            ('SU', 'Sunday'),
            ('MO', 'Monday'),
            ('TU', 'Tuesday'),
            ('WE', 'Wednesday'),
            ('TH', 'Thursday'),
            ('FR', 'Friday'),
            ('SA', 'Saturday'),
        ],
        validators=[Optional()],
    )
    # Cannot use until and count together
    count = IntegerField(
        'Number of Transactions',
        validators=[NumberRange(min=1, max=100), Optional()],
    )
    until = DateField('End Date', validators=[Optional()])
    change = RadioField(
        'Change',
        choices=[
            ('current', 'Current transaction'),
            ('all', 'All transactions in the series'),
            ('after', 'All following transactions'),
        ],
        validators=[Optional()],
    )

    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    delete = SubmitField('Delete')

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
                raise ValidationError(
                    "Select 'End Date' or 'Number of Transactions', but not both.")
            if until.data < self.date.data:
                raise ValidationError(
                    'Please use an end date after the transaction date.')
