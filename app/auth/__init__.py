import flask

bp = flask.Blueprint('auth', __name__)

from app.auth import routes
