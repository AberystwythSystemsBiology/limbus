from flask import redirect, abort, render_template, url_for, session, request, jsonify

from . import pcf
from .. import db
from .forms import NewConsentFormTemplate
from ..misc.generators import generate_random_hash

@pcf.route("/")
def index():
    return render_template("patientconsentform/index.html")

@pcf.route("/add", methods=["GET", "POST"])
def new():
    form = NewConsentFormTemplate()

    if form.validate_on_submit():
        hash = generate_random_hash()
        session["%s consent_form_info" % (hash)] = {
            "template_name": form.name.data
        }

        return redirect(url_for('pcf.new_two', hash=hash))

    return render_template("patientconsentform/add/one.html", form=form)

@pcf.route("/add/two/<hash>", methods=["GET", "POST"])
def new_two(hash):
    if request.method == "POST":
        resp = jsonify({"redirect": url_for('pcf.index', _external=True)})
        return resp, 200, {'ContentType':'application/json'}
    return render_template("patientconsentform/add/two.html")
