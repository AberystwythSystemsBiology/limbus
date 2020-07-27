from __future__ import absolute_import
import os


from flask import Flask, g, render_template

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_continuum.plugins import PropertyModTrackerPlugin

db = SQLAlchemy()
ma = Marshmallow()

from .base import Base

Base = declarative_base(cls=Base)
Base.query = db.session.query_property()

login_manager = LoginManager()

make_versioned(user_cls=None, plugins=[FlaskPlugin(), PropertyModTrackerPlugin()])

# Blueprint imports:
# from .admin import admin as admin_blueprint
from .misc import misc as misc_blueprint
'''
from .attribute import attribute as attribute_blueprint
'''
from .setup import setup as setup_blueprint
from .auth import auth as auth_blueprint
'''
from .document import document as doc_blueprint
from .sample import sample as sample_blueprint
from .donor import donor as donor_blueprint
from .patientconsentform import pcf as pcf_blueprint
from .processing import processing as processing_blueprint
from .storage import storage as storage_blueprint
from .procedure import procedure as procedure_blueprint
'''

from .commands import cmd_setup as cmd_setup_blueprint

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile("config.py")

    db.init_app(app)
    ma.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"


    # Models imports:
    from app.misc import models as misc_models
    from app.auth import models as auth_models

    '''
    from app.document import models as doc_models
    from app.sample import models as sample_models
    from app.patientconsentform import models as pcf_models
    from app.processing import models as processing_models
    from app.storage import models as storage_models
    from app.attribute import models as attribute_models
    from app.donor import models as donor_models
    from app.procedure import models as procedure_models
    '''

    orm.configure_mappers()


    app.register_blueprint(misc_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(setup_blueprint, url_prefix="/setup")
    '''
    app.register_blueprint(admin_blueprint, url_prefix="/admin")
    app.register_blueprint(attribute_blueprint, url_prefix="/attributes")
    app.register_blueprint(processing_blueprint, url_prefix="/processing")
    app.register_blueprint(doc_blueprint, url_prefix="/documents")
    app.register_blueprint(sample_blueprint, url_prefix="/samples")
    app.register_blueprint(donor_blueprint, url_prefix="/donors")
    app.register_blueprint(pcf_blueprint, url_prefix="/pcf")
    app.register_blueprint(storage_blueprint, url_prefix="/storage")
    app.register_blueprint(procedure_blueprint, url_prefix="/procedures")
    '''


    # Command line blueprints.
    app.register_blueprint(cmd_setup_blueprint)

    from app.errors import error_handlers

    for error_handler in error_handlers:
        app.register_error_handler(
            error_handler["code_or_exception"], error_handler["func"]
        )


    return app
