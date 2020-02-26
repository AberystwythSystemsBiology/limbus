from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user

from .. import processing

from ..forms import NewProtocolForm, FluidCheckList

@processing.route("/protocols")
def protocol_index():
    return render_template("processing/protocols/index.html")


@processing.route("/protocols/new", methods=["GET", "POST"])
def new_protocol():
    form = NewProtocolForm()
    return render_template("processing/protocols/new/one.html", form=form)

@processing.route("/protocols/new/two/<hash>")
def new_protocol_two(hash):
    pass