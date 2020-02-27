from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user

from .. import processing

from ..forms import NewProtocolForm, FluidCheckList, ProcessingInformation

from ...misc.generators import generate_random_hash


from ..models import *

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
            "type": form.type.data,
        }

        return redirect(url_for("processing.new_protocol_two", hash=protocol_hash))

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
                "post_cent": form.pd.data,
            }

            return redirect(url_for("processing.new_protocol_three", hash=hash))

    else:
        return abort(501)

    return render_template("processing/protocols/new/two.html", hash=hash, form=form)


def _submit_fluid_protocol(info, steps, form) -> None:
    
    
    u_id = current_user.id
    

    pi = ProcessingTemplate(
        name = info["name"],
        sample_type = info["type"],
        author_id = u_id
    )

    db.session.add(pi)
    db.session.flush()

    ptfc = ProcessingTemplateFluidContainer(
        container = form.container.data,
        template_id = pi.id,
        author_id = u_id
    )

    db.session.add(ptfc)
    db.session.flush()

    if steps["pre_cent"]:
        pci = PreCentrifugeInformation(
            temp = form.pre_centr_temp,
            time = form.pre_centr_time,
            template_id = pi.id,
            uploader = u_id
        )

        db.session.add(pci)

    if steps["cent"]:
        ci = CentrifugeInformation(
            temp = form.centr_temp.data,
            time = form.centr_time.data,
            weight = form.centr_weight.data,
            braking = form.centr_braking.data,
            template_id = pi.id,
            second = False,
            uploader = u_id
        )

        db.session.add(ci)
        db.session.flush()


        if steps["sec_cent"]:
            sci = CentrifugeInformation(
                temp = form.sec_centr_temp.data,
                time = form.sec_centr_time.data,
                weight = form.sec_centr_weight.data,
                braking = form.sec_centr_braking.data,
                template_id = pi.id,
                second = True,
                uploader = u_id
            )

            db.session.add(sci)
            db.session.flush()

        

    if steps["post_cent"]:
        pci = PostCentrifugeInformation(
            temp = form.post_centr_temp,
            time = form.post_centr_time,
            template_id = pi.id,
            uploader = u_id
        )

        db.session.add(pci)

    db.session.commit()


@processing.route("/protocols/new/three/<hash>", methods=["GET", "POST"])
def new_protocol_three(hash):

    info = session["%s protocol_information" % (hash)]
    sample_type = session["%s protocol_information" % (hash)]["type"]
    steps = session["%s steps" % (hash)]

    form = ProcessingInformation(sample_type, steps)

    if form.validate_on_submit():

        if sample_type == "FLU":
            _submit_fluid_protocol(info, steps, form)

        return redirect(url_for('processing.protocols_index'))

    return render_template(
        "processing/protocols/new/three.html", hash=hash, form=form, steps=steps
    )
