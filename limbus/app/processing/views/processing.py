from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user

from .. import processing

from ..forms import NewProtocolForm, FluidCheckList, ProcessingInformation

from ...misc.generators import generate_random_hash

from ... import db
from ...auth.models import User

from ..models import *

@processing.route("/protocols")
def protocol_index():
    protocols = db.session.query(ProcessingTemplate, User).filter(
        ProcessingTemplate.author_id == User.id
    ).all()

    return render_template("processing/protocols/index.html", protocols=protocols)


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



@processing.route("/protocols/view/LIMBPRO-<protocol_id>")
def view_protocol(protocol_id):
    _protocol = db.session.query(ProcessingTemplate).filter(ProcessingTemplate.id == protocol_id).first()

    if _protocol.sample_type == SampleType.FLU:
        _container = db.session.query(ProcessingTemplateFluidContainer).filter(ProcessingTemplateFluidContainer.template_id == _protocol.id).first_or_404()
        _pre_centr = db.session.query(PreCentrifugeInformation).filter(PreCentrifugeInformation.template_id == _protocol.id).first()
        _cent = db.session.query(CentrifugeInformation).filter(CentrifugeInformation.template_id == _protocol.id).all()
        _post = db.session.query(PostCentrifugeInformation).filter(PostCentrifugeInformation.template_id == _protocol.id).first_or_404()

        class Protocol:
            def __init__(self):
                self._prepare_template()
                self._prepare_container()
                self._prepare_pre_centr()
                self._prepare_centr()
                self._prepare_post_centre()

            def _prepare_template(self):
                self.id = _protocol.id
                self.template_info = {
                    "template_name": _protocol.name,
                    "sample_type": _protocol.sample_type
                }

            def _prepare_container(self):
                self.container_info = {
                    "type": _container.container
                }

            def _prepare_pre_centr(self):
                if _pre_centr != None:
                    self.pre_centr_info = {
                        "temp": _pre_centr.temp,
                        "time": _pre_centr.time
                    }
                else:
                    self.pre_centr_info = False

            def _prepare_centr(self):
                self.centr = False
                self.sec_centr = False
                for centr in _cent:
                    centr_info = {
                        "temp": centr.temp,
                        "time": centr.time,
                        "weight": centr.weight,
                        "braking": centr.weight,
                        "second": centr.second
                    }
                    if not centr.second:
                        self.centr = centr_info
                    else:
                        self.sec_centr = centr_info

            def _prepare_post_centre(self):
                self.post_centr = False
                if _post != None:
                    self.post_centr = {
                        "temp": _post.temp,
                        "time": _post.time
                    }



    return render_template("processing/protocols/view.html", protocol=Protocol())


@processing.route("/protocols/new/three/<hash>", methods=["GET", "POST"])
def new_protocol_three(hash):

    info = session["%s protocol_information" % (hash)]
    sample_type = session["%s protocol_information" % (hash)]["type"]
    steps = session["%s steps" % (hash)]

    form = ProcessingInformation(sample_type, steps)

    if form.validate_on_submit():

        if sample_type == "FLU":
            pi = ProcessingTemplate(
                name=info["name"],
                sample_type=info["type"],
                author_id=1
            )

            db.session.add(pi)
            db.session.flush()

            ptfc = ProcessingTemplateFluidContainer(
                container=form.container.data,
                template_id=pi.id,
                author_id=current_user.id
            )

            db.session.add(ptfc)
            db.session.flush()

            if steps["pre_cent"]:
                pci = PreCentrifugeInformation(
                    temp=form.pre_centr_temp.data,
                    time=form.pre_centr_time.data,
                    template_id=pi.id,
                    author_id=current_user.id
                )

                db.session.add(pci)

            if steps["cent"]:
                ci = CentrifugeInformation(
                    temp=form.centr_temp.data,
                    time=form.centr_time.data,
                    weight=form.centr_weight.data,
                    braking=form.centr_braking.data,
                    template_id=pi.id,
                    second=False,
                    author_id=current_user.id
                )

                db.session.add(ci)
                db.session.flush()

                if steps["sec_cent"]:
                    sci = CentrifugeInformation(
                        temp=form.sec_centr_temp.data,
                        time=form.sec_centr_time.data,
                        weight=form.sec_centr_weight.data,
                        braking=form.sec_centr_braking.data,
                        template_id=pi.id,
                        second=True,
                        author_id=current_user.id
                    )

                    db.session.add(sci)
                    db.session.flush()

            if steps["post_cent"]:
                pci = PostCentrifugeInformation(
                    temp=form.post_centr_temp.data,
                    time=form.post_centr_time.data,
                    template_id=pi.id,
                    author_id=current_user.id
                )

                db.session.add(pci)

            db.session.commit()

        return redirect(url_for('processing.protocol_index'))

    return render_template(
        "processing/protocols/new/three.html", hash=hash, form=form, steps=steps
    )
