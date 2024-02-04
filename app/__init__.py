from flask_login import LoginManager
from flask import Flask, g
from app.db.database import session as db
from app.db.database import init_db

from app.forms.auth_forms import UserForm
from app.routes.auth import auth_routes
from app.routes.main import main_routes
from app.db.user import get_user, add_user
from app.utilities.limiter import limiter
from dotenv import load_dotenv


def create_app():
    load_dotenv('secrets.env')
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Register blueprints for the routes
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)

    # Load secret key
    app.config.from_pyfile('config.py')

    # Initialize the login manager
    lm = LoginManager(app)
    lm.login_view = "auth.login"
    lm.session_protection = "strong"
    lm.init_app(app)

    # Initialize the database
    init_db()


    @lm.user_loader
    def load_user(user_id):
        user = get_user(user_id)
        return user

    limiter.init_app(app)

    @app.teardown_appcontext
    def close_db(exception):
        _db = getattr(g, '_database', None)
        if _db is not None:
            _db.close()

    # Sets the security headers for the application
    @app.after_request
    def add_security_headers(response):
        csp = {
            "default-src": "'self'",
            "script-src": [
                "'self'",
                "https://code.jquery.com/jquery-3.5.1.slim.min.js",
                "https://cdn.jsdelivr.net/npm/popper.js@1.9.2/dist/umd/popper.min.js",
                "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js",
                "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
                "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js",
                "https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js",
            ],
            "style-src": [
                "'self'",
                "https://maxcdn.bootstrapcdn.com",
                "https://stackpath.bootstrapcdn.com",
            ],
            "img-src": [
                "'self'",
                "data:",
                "https://cdn.pixabay.com"
            ],
            "form-action": [
                "'self'"
            ],
            "object-src": "'none'",
        }

        rules = "; ".join(
            [" ".join([directive] + list(sources)) for directive, sources in csp.items()]
        )

        response.headers['Content-Security-Policy'] = rules
        return response
    return app