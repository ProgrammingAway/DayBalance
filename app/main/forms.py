from wtforms import Form, StringField, BooleanField
from wtforms import DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.fields.html5 import DateField
from app.models import User
from flask_login import current_user

class TransactionForm(Form):
    title = StringField('Transaction Name', validators=[DataRequired()])
    date = DateField('Transaction Date', validators=[DataRequired()])
    amount = DecimalField('Transaction Amount', validators=[DataRequired()], places=2)
    description = TextAreaField('Description', validators=[Length(min=0, max=140)])
    income = BooleanField('Income')
#    is_recurring = BooleanField('Recurring')
#    freq = SelectField('Frequency', choices=[('Yearly'), ('Monthly'), ('Weekly'), ('Daily')])
#    interval = DecimalField('Frequency Interval', validators=[NumberRange(min=1, max=100], places=0)
#    wkst = SelectMultipleField('Day of the Week', choices=[('SU'), ('MO'), ('TU'), ('WE'), ('TH'), ('FR'), ('SA')])
#    count = DecimalField('Number of Transactions', validators=[NumberRange(min=1, max=100], places=0)  # (Cannot be used with until)
#    until = DateField('End Date')  # (Cannot be used with count)
    submit = SubmitField('Submit')

    def validate_date(self, date):
        start_date = current_user.start_date
        if date.data < start_date:
            raise ValidationError(
                'Please use a date after the budget start date: '
                + str(start_date) + '.'
            )

    def validate_until(self, until):
        if self.count.data and until.data:
            raise ValidationError("Select 'End Date' or 'Number of Transactions', but not both.")
        if until.data < self.date.data:
            raise ValidationError('Please use an end date after the transaction date.')
            
    def validate_count(self, count):
        
