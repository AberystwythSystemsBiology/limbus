# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import absolute_import

from .database import db

from flask import Flask

from .commands import cmd_setup as cmd_setup_blueprint
from .api import api as api_blueprint
from .labels import labels as label_blueprint
from .setup import setup as setup_blueprint
from .misc import misc as misc_blueprint
from .auth import auth as auth_blueprint
from .attribute import attribute as attribute_blueprint
from .document import document as document_blueprint
from .procedure import procedure as procedure_blueprint
from .donor import donor as donor_blueprint
from .consent import consent as consent_blueprint
from .protocol import protocol as protocol_blueprint
from .sample import sample as sample_blueprint
from .tmpstore import tmpstore as tmpstore_blueprint
from .storage import storage as storage_blueprint
from .admin import admin as admin_blueprint
from .event import event as event_blueprint

from .errors import error_handlers

from .extensions import register_extensions, register_apispec


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


def register_blueprints(app):
    app.register_blueprint(cmd_setup_blueprint)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(label_blueprint, url_prefix="/labels")
    app.register_blueprint(setup_blueprint, url_prefix="/setup")
    app.register_blueprint(misc_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(attribute_blueprint, url_prefix="/attribute")
    app.register_blueprint(document_blueprint, url_prefix="/document")
    app.register_blueprint(procedure_blueprint, url_prefix="/procedure")
    app.register_blueprint(event_blueprint, url_prefix="/event")
    app.register_blueprint(donor_blueprint, url_prefix="/donor")
    app.register_blueprint(consent_blueprint, url_prefix="/consent")
    app.register_blueprint(protocol_blueprint, url_prefix="/protocol")
    app.register_blueprint(sample_blueprint, url_prefix="/sample")
    app.register_blueprint(tmpstore_blueprint, url_prefix="/tmpstore")
    app.register_blueprint(storage_blueprint, url_prefix="/storage")
    app.register_blueprint(admin_blueprint, url_prefix="/admin")


def setup_database(app):
    with app.app_context():
        db.create_all()
