import flask

bp = flask.Blueprint('errors', __name__)

from app.errors import handlers
