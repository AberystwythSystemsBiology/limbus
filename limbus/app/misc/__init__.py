from flask import Blueprint, render_template

misc = Blueprint("misc", __name__)

@misc.route("/")
def index():
    return render_template("misc/index.html")