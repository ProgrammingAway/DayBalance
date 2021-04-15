from wtforms import Form, StringField, BooleanField
from wtforms import DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.fields.html5 import DateField
from app.models import User
from flask_login import current_user

class TransactionForm(Form):
    title = StringField('Transaction Name', validators=[DataRequired()])
    date = DateField('Transaction Date', validators=[DataRequired()])
    amount = DecimalField('Transaction Amount', validators=[DataRequired()],
        places=2)
    description = TextAreaField('Description',
        validators=[Length(min=0, max=140)])
    income = BooleanField('Income')
    submit = SubmitField('Submit')

    def validate_date(self, date):
        start_date = current_user.start_date
        if date.data < start_date:
            raise ValidationError(
                'Please use a date after the budget start date: '
                + str(start_date) + '.'
            )

