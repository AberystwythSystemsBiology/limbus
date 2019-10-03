from functools import wraps

from flask import redirect, render_template, url_for, flash, abort
from flask_admin.contrib.sqla import ModelView

from .. import db
from ..auth.models import User

def add_admin_views():
    from .. import app_admin
    app_admin.add_view(ModelView(User, db.session))
