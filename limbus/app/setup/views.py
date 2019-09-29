from flask import redirect, render_template, url_for

from ..auth.models import User

from . import setup
from .. import db
from .forms import LoginForm

@setup.route("/")
def index():
    return render_template("setup/index.html")
