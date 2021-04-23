import app
import app.models

app = app.create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': app.db, 'User': app.models.User, 'Transaction': app.models.Transaction}
