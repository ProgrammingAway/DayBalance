import flask
import app.email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    app.email.send_email('[DayBalance] Reset Your Password',
        sender=flask.current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=flask.render_template(
            'email/reset_password.txt',
            user=user,
            token=token,
        ),
        html_body=flask.render_template(
            'email/reset_password.html',
            user=user,
            token=token,
        ),
    )
