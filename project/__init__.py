from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta
from pathlib import Path
from flask_admin import Admin
from werkzeug.security import generate_password_hash


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
admin = Admin()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-do-not-reveal'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photos.db'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120) # Added session timeout timer
    CWD = Path(os.path.dirname(__file__))
    app.config['UPLOAD_DIR'] = CWD / "uploads"

    db.init_app(app)
    admin.init_app(app)
    

    login_manager = LoginManager()
    login_manager.login_view = 'authentication.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for auth routes in our app
    from .authentication import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
