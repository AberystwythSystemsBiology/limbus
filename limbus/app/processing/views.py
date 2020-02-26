from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user

from . import processing

@processing.route("/")
def index():
    return render_template("processing/index.html")
