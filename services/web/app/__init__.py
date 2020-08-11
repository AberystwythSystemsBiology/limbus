from __future__ import absolute_import

from .database import db
from flask import Flask

from flask_mde import Mde

from flask_login import LoginManager
from flask_marshmallow import Marshmallow


from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin as apispec_FlaskPlugin

from .commands import cmd_setup as cmd_setup_blueprint
from .api import api as api_blueprint
from .setup import setup as setup_blueprint
from .misc import misc as misc_blueprint
from .auth import auth as auth_blueprint
from .attribute import attribute as attribute_blueprint
from .document import document as document_blueprint
from .consent import consent as consent_blueprint
from .protocol import protocol as protocol_blueprint
from .sample import sample as sample_attribute

from app.errors import error_handlers

spec = APISpec(
    title="LImBuS API Documentation",
    version="20.08",
    openapi_version="3.0.2",
    plugins=[apispec_FlaskPlugin(), MarshmallowPlugin()]
)


ma = Marshmallow()
mde = Mde()
login_manager = LoginManager()

from .api import *

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_apispec(app)
    return app

def register_error_handlers(app):
    for error_handler in error_handlers:
        app.register_error_handler(
            error_handler["code_or_exception"], error_handler["func"]
        )

def register_apispec(app):

    with app.test_request_context():
        spec.path(view=auth_new_user)
        spec.path(view=auth_home)

def register_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    mde.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

def register_blueprints(app):
    app.register_blueprint(cmd_setup_blueprint)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(setup_blueprint, url_prefix="/setup")
    app.register_blueprint(misc_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(attribute_blueprint, url_prefix="/attribute")
    app.register_blueprint(document_blueprint, url_prefix="/document")
    app.register_blueprint(consent_blueprint, url_prefix="/consent")
    app.register_blueprint(protocol_blueprint, url_prefix="/protocol")
    app.register_blueprint(sample_attribute, url_prefix="/sample")

def setup_database(app):
    with app.app_context():
        db.create_all()
