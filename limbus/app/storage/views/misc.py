from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage


@storage.route("/")
def index():
    return render_template("storage/index.html")