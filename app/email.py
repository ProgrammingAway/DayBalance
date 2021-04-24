import threading
import flask
import flask_mail
import app


def send_async_email(app, msg):
    with app.app_context():
        app.mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = flask_mail.Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        app.mail.send(msg)
    else:
        threading.Thread(
            target=send_async_email,
            args=(flask.current_app._get_current_object(), msg),
        ).start()
