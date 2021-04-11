from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    start_date = DateField('Transaction Date', validators=[DataRequired()])
    start_balance = DecimalField('Transaction Amount', validators=[DataRequired()], places=2)
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class TransactionForm(FlaskForm):
    title = StringField('Transaction Name', validators=[DataRequired()])
    date = DateField('Transaction Date', validators=[DataRequired()])
    amount = DecimalField('Transaction Amount', validators=[DataRequired()], places=2)
    description = TextAreaField('Description', validators=[Length(min=0, max=140)])
    income = BooleanField('Income')


