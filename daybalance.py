import app
from app import db
from app.models import User, Transaction

app = app.create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Transaction': Transaction,
    }
