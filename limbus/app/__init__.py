from flask import Flask, g

from config import app_config

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()

# blueprint imports
from .misc import misc as misc_blueprint
from .setup import setup as setup_blueprint
from .auth import auth as auth_blueprint

def create_app(flask_config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[flask_config])
    app.config.from_pyfile("config.py")
    
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    migrate = Migrate(app, db)

    # Load in models here
    from app.auth import models as auth_models
    
    app.register_blueprint(misc_blueprint)
    app.register_blueprint(setup_blueprint)
    app.register_blueprint(auth_blueprint)

    return app