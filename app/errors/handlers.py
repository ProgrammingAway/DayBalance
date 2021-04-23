import flask
import app
import app.errors


@app.errors.bp.app_errorhandler(404)
def not_found_error(error):
    return flask.render_template('errors/404.html'), 404


@app.errors.bp.app_errorhandler(500)
def internal_error(error):
    app.db.session.rollback()
    return flask.render_template('errors/500.html'), 500
