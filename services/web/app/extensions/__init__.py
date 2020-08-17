from flask_mde import Mde
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

from ..database import db, UserAccount

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin as apispec_FlaskPlugin


spec = APISpec(
    title="LImBuS API Documentation",
    version="20.08",
    openapi_version="3.0.2",
    plugins=[apispec_FlaskPlugin(), MarshmallowPlugin()],
)

ma = Marshmallow()
mde = Mde()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    mde.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: int) -> UserAccount:
        return UserAccount.query.get(user_id)


from ..api import *


def register_apispec(app):

    with app.test_request_context():
        #spec.path(view=auth_new_user)
        pass
    
