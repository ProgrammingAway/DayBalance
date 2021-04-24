import os
import logging
import logging.handlers
import flask
import flask_sqlalchemy
import flask_migrate
import flask_login
import flask_mail
import calendar
import config

db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()
login = flask_login.LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = flask_mail.Mail()
balance_calendar = calendar.Calendar()


def create_app(config_class=config.Config):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    if app.config['START_MONDAY']:
        balance_calendar.setfirstweekday(0)  # 0 = Monday, 6 = Sunday
    else:
        balance_calendar.setfirstweekday(6)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = logging.handlers.SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = logging.handlers.RotatingFileHandler(
                'logs/daybalance.log',
                maxBytes=10240,
                backupCount=10,
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('DayBalance startup')

    return app


from app import models
