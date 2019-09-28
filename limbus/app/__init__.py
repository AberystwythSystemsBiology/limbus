from flask import Flask, g

from config import app_config

# blueprint imports
from .misc import misc as misc_blueprint


def create_app(flask_config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[flask_config])
    app.config.from_pyfile("config.py")
      
    app.register_blueprint(misc_blueprint)

    return app