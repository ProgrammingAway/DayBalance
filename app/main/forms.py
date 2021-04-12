from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DecimalField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, InputRequired
from wtforms.fields.html5 import DateField
from app.models import User


class TransactionForm(FlaskForm):
    title = StringField('Transaction Name', validators=[DataRequired()])
    date = DateField('Transaction Date', validators=[DataRequired()])
    amount = DecimalField('Transaction Amount', validators=[DataRequired()], places=2)
    description = TextAreaField('Description', validators=[Length(min=0, max=140)])
    income = BooleanField('Income')
    submit = SubmitField('Submit')
