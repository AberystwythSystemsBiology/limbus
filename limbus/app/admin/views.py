from functools import wraps

from flask import redirect, render_template, url_for, flash, abort
from flask_admin.contrib.sqla import ModelView

from .. import db
from ..auth.models import User
from ..setup.models import Biobank

class UserView(ModelView):
    column_exclude_list=["password_hash"]

def add_admin_views():
    from .. import app_admin
    app_admin.add_view(UserView(User, db.session))
    app_admin.add_view(ModelView(Biobank, db.session))
