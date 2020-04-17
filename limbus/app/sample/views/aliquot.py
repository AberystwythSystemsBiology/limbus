from flask import render_template, redirect, session, url_for, request, jsonify
from .. import sample
from flask_login import login_required, current_user


@sample.route("view/LIMBSMP-<sample_id>/aliquot", methods=["GET", "POST"])
@login_required
def aliquot(sample_id):
    return render_template("sample/sample/aliquot/create.html")
