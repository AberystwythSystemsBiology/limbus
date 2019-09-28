from flask import Flask

from config import app_config

def create_app(flask_config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[flask_config])
    app.config.from_pyfile("config.py")

    from .misc import misc as misc_blueprint
    app.register_blueprint(misc_blueprint)

    return app