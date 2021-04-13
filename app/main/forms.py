from wtforms import Form, StringField, BooleanField
from wtforms import DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import DateField
from app.models import User


class TransactionForm(Form):
    title = StringField('Transaction Name', validators=[DataRequired()])
    date = DateField('Transaction Date', validators=[DataRequired()])
    amount = DecimalField('Transaction Amount', validators=[DataRequired()],
        places=2)
    description = TextAreaField('Description',
        validators=[Length(min=0, max=140)])
    income = BooleanField('Income')
    submit = SubmitField('Submit')
