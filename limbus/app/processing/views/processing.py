from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user

from .. import processing

from ..forms import NewProtocolForm, FluidCheckList, ProcessingInformation

from ...misc.generators import generate_random_hash


@processing.route("/protocols")
def protocol_index():
    return render_template("processing/protocols/index.html")


@processing.route("/protocols/new", methods=["GET", "POST"])
def new_protocol():
    form = NewProtocolForm()
    if form.validate_on_submit():
        protocol_hash = generate_random_hash()

        session["%s protocol_information" % (protocol_hash)] = {
            "name": form.name.data,
            "type": form.type.data
        }

        return redirect(url_for('processing.new_protocol_two', hash=protocol_hash))

    return render_template("processing/protocols/new/one.html", form=form)

@processing.route("/protocols/new/two/<hash>", methods=["GET", "POST"])
def new_protocol_two(hash):

    if session["%s protocol_information" % (hash)]["type"] == "FLU":
        form = FluidCheckList()

        if form.validate_on_submit():
            session["%s steps" % (hash)] = {
                "pre_cent": form.pc.data,
                "cent": form.ce.data,
                "sec_cent": form.sc.data,
                "post_cent": form.pd.data
            }

            return redirect(url_for('processing.new_protocol_three', hash=hash))



    else:
        return abort(501)

    return render_template("processing/protocols/new/two.html", hash=hash, form=form)
    

    
@processing.route("/protocols/new/three/<hash>", methods=["GET", "POST"])
def new_protocol_three(hash):

    sample_type = session["%s protocol_information" % (hash)]["type"]
    steps = session["%s steps" % (hash)]

    form = ProcessingInformation(sample_type, steps)


    if form.validate_on_submit():
        pass

    return render_template("processing/protocols/new/three.html", hash=hash, form=form, steps=steps)