from wtforms import Form, StringField, PasswordField, BooleanField
from wtforms import DecimalField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, InputRequired
from wtforms.validators import Email, EqualTo
from wtforms.fields.html5 import DateField
from app.models import User


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()],
        render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],
        render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(Form):
    username = StringField('Username', validators=[DataRequired()],
        render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Email Address"})
    password = PasswordField('Password', validators=[DataRequired()],
        render_kw={"placeholder": "Password"})
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),
        EqualTo('password')], render_kw={"placeholder": "Password (again)"})
    start_date = DateField('Initial Date', validators=[InputRequired()])
    start_balance = DecimalField('Initial Balance',
        validators=[DataRequired()], places=2)
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Email Address"})
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()],
        render_kw={"placeholder": "Password"})
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),
        EqualTo('password')], render_kw={"placeholder": "Password (again)"})
    submit = SubmitField('Request Password Reset')
