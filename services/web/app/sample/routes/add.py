# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import render_template, redirect, session, url_for, flash, abort
from flask_login import login_required, current_user

from ...misc import get_internal_api_header

import uuid
from .. import sample

from ..forms import CollectionConsentAndDisposalForm

import requests

@sample.route("add/<hash>", methods=["GET"])
@login_required
def add_rerouter(hash):
    if hash == "new":
        return redirect(url_for("sample.add_collection_consent_and_barcode"))



@sample.route("add/one", methods=["GET", "POST"])
@login_required
def add_collection_consent_and_barcode():
    consent_templates = []
    collection_protocols = []
    processing_protocols = []

    consent_templates_response = requests.get(
        url_for("api.consent_query", _external=True),
        headers= get_internal_api_header(),
        json={"is_locked": False}
    )

    if consent_templates_response.status_code == 200:
        for template in consent_templates_response.json()["content"]:
            consent_templates.append([template["id"], "LIMBPCF-%i: %s" % (template["id"], template["name"])])


    protocols_response = requests.get(
        url_for("api.protocol_query", _external=True),
        headers= get_internal_api_header(),
        json={"is_locked": False}
    )

    if protocols_response.status_code == 200:
        for protocol in protocols_response.json()["content"]:
            if protocol["type"] == "ACQ":
                collection_protocols.append([protocol["id"], "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"])])
            elif protocol["type"] == "SAP":
                processing_protocols.append([protocol["id"], "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"])])

    form = CollectionConsentAndDisposalForm(consent_templates, collection_protocols)

    if form.validate_on_submit():
        sample_add_hash = uuid.uuid4()

        route_data = {
            "barcode": form.barcode.data,
            "collection_protocol_id": form.collection_select.data,
            "collected_by": form.collected_by.data,
            "consent_form_id": form.consent_select.data,
            "collection_date": form.collection_date.data,
            "disposal_instruction": form.disposal_instruction.data,
            "disposal_date": form.disposal_date.data,
            "has_donor": form.has_donor.data,
        }

        # This needs to be broken out to a new module then...

        tss = TemporarySampleStore(
            uuid=sample_add_hash,
            data={
                "add_collection_consent_and_barcode": route_data
            },
            author_id = current_user.id
        )

        db.session.add(tss)
        db.session.commit()

        return redirect(
            url_for("sample.add_rerouter", hash=sample_add_hash))

    return render_template(
        "sample/sample/add/step_one.html",
        form=form,
        template_count=len(consent_templates),
        collection_protocol_count=len(collection_protocols),
        processing_protocols_count=len(processing_protocols)
    )


'''
@sample.route("add/two/<hash>", methods=["GET", "POST"])
@login_required
def fill_digital_consent_form(hash):
    t_id = session["%s step_one" % (hash)]["consent_form_id"]

    pcf = (
        db.session.query(ConsentFormTemplate)
        .filter(ConsentFormTemplate.id == t_id)
        .first_or_404()
    )

    pcf_questions = (
        db.session.query(ConsentFormTemplateQuestion)
        .filter(ConsentFormTemplateQuestion.template_id == t_id)
        .all()
    )

    questionnaire = PatientConsentQuestionnaire(pcf_questions)

    if questionnaire.validate_on_submit():

        checked = []
        for q in questionnaire:
            if q.type == "BooleanField":
                if q.data:
                    checked.append(int(q.name))

        session["%s step_two" % (hash)] = {
            "consent_id": questionnaire.consent_id.data,
            "checked": checked,
        }

        return redirect(url_for("sample.select_sample_type", hash=hash))

    return render_template(
        "sample/sample/add/step_two.html",
        hash=hash,
        pcf=pcf,
        questionnaire=questionnaire,
    )


@sample.route("add/three/<hash>", methods=["GET", "POST"])
@login_required
def select_sample_type(hash):
    form = SampleTypeSelectForm()

    if form.validate_on_submit():
        a = {"sample_type": form.sample_type.data, "quantity": form.quantity.data}

        if a["sample_type"] == "CEL":
            b = {
                "type": form.cell_sample_type.data,
                "fixation": form.fixation_type.data,
                "storage_type": form.cell_container.data,
            }
        elif a["sample_type"] == "FLU":
            b = {
                "type": form.fluid_sample_type.data,
                "storage_type": form.fluid_container.data,
            }
        elif a["sample_type"] == "MOL":
            b = {
                "type": form.molecular_sample_type.data,
                "storage_type": form.fluid_container.data,
            }

        data = {**a, **b}

        session["%s step_three" % (hash)] = data

        return redirect(url_for("sample.select_processing_protocol", hash=hash))

    return render_template("sample/sample/add/step_three.html", form=form, hash=hash)


@sample.route("add/four/<hash>", methods=["GET", "POST"])
def select_processing_protocol(hash):
    templates = (
        db.session.query(ProcessingTemplate)
        .filter(
            ProcessingTemplate.sample_type.in_(
                [session["%s step_three" % (hash)]["sample_type"], "ALL"]
            )
        )
        .all()
    )
    form = ProtocolTemplateSelectForm(templates)

    if form.validate_on_submit():
        session["%s step_four" % (hash)] = {
            "protocol_id": form.form_select.data,
            "sample_status": form.sample_status.data,
            "processing_date": form.processing_date.data,
            "processing_time": form.processing_time.data.strftime("%H:%M:%S"),
        }
        return redirect(url_for("sample.add_sample_attr", hash=hash))

    return render_template(
        "sample/sample/add/step_four.html",
        templates=len(templates),
        form=form,
        hash=hash,
    )


@sample.route("add/five/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_attr(hash):
    form = CustomAttributeSelectForm(CustomAttributeElementTypes.SAMPLE)

    if form.validate_on_submit():
        attribute_ids = []
        for e in form:
            if e.type == "BooleanField" and e.data:
                attribute_ids.append(str(e.id))

        session["%s step_five" % (hash)] = attribute_ids
        return redirect(url_for("sample.add_sample_form", hash=hash))

    return render_template(
        "sample/sample/add/step_five.html",
        form=form,
        hash=hash,
        num_attr=len([e for e in form if e.type == "BooleanField"]),
    )


@sample.route("add/six/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_form(hash):
    attributes = session["%s step_five" % (hash)]

    form = CustomAttributeGeneratedForm(FinalSampleForm(), attributes)

    # Submit if no attributes found.
    if form.validate_on_submit() or len(attributes) == 0:
        # consent_form_id, barcode, collection_date, disposal_instruction, disposal_date, has_donor, donor_select
        step_one = session["%s step_one" % (hash)]
        # checked, consent_id
        step_two = session["%s step_two" % (hash)]
        # sample_type, quantity, type, fixation, storage_type
        step_three = session["%s step_three" % (hash)]
        # protocol_id, sample_status, processing_date, processing_time
        step_four = session["%s step_four" % (hash)]
        # attribute_ids
        step_five = session["%s step_five" % (hash)]

        sample = Sample(
            uuid=uuid.uuid4(),
            biobank_barcode=step_one["barcode"],
            sample_type=step_three["sample_type"],
            collection_date=step_one["collection_date"],
            quantity=step_three["quantity"],
            current_quantity=step_three["quantity"],
            is_closed=False,
            author_id=current_user.id,
            sample_status=step_four["sample_status"],
        )

        db.session.add(sample)
        db.session.flush()

        sdi = SampleDisposalInformation(
            disposal_instruction=step_one["disposal_instruction"],
            disposal_date=step_one["disposal_date"],
            sample_id=sample.id,
            author_id=current_user.id,
        )

        db.session.add(sdi)
        db.session.flush()

        if step_one["has_donor"]:

            std = SampleToDonor(
                sample_id=sample.id,
                donor_id=step_one["donor_select"],
                author_id=current_user.id,
            )

            db.session.add(std)
            db.session.flush()

        if step_three["sample_type"] == "FLU":
            stot = SampleToFluidSampleType(
                sample_id=sample.id,
                sample_type=step_three["type"],
                author_id=current_user.id,
            )
        elif step_three["sample_type"] == "CEL":
            stot = SampleToCellSampleType(
                sample_id=sample.id,
                sample_type=step_three["type"],
                author_id=current_user.id,
            )
        elif step_three["sample_type"] == "MOL":
            stot = SampleToMolecularSampleType(
                sample_id=sample.id,
                sample_type=step_three["type"],
                author_id=current_user.id,
            )
        else:
            abort(400)

        db.session.add(stot)
        db.session.flush()

        for attr in form:
            if hasattr(attr, "render_kw") and attr.render_kw != None:
                if "_custom_val" in attr.render_kw:
                    if attr.type == "StringField":
                        ca_v = SampleToCustomAttributeTextValue(
                            value=attr.data,
                            custom_attribute_id=attr.id,
                            sample_id=sample.id,
                            author_id=current_user.id,
                        )

                    elif attr.type == "SelectField":
                        ca_v = SampleToCustomAttributeOptionValue(
                            custom_option_id=attr.data,
                            custom_attribute_id=attr.id,
                            sample_id=sample.id,
                            author_id=current_user.id,
                        )
                    else:
                        ca_v = SampleToCustomAttributeNumericValue(
                            value=attr.data,
                            custom_attribute_id=attr.id,
                            sample_id=sample.id,
                            author_id=current_user.id,
                        )

                    db.session.add(ca_v)

        db.session.flush()

        spcfta = SamplePatientConsentFormTemplateAssociation(
            sample_id=sample.id,
            template_id=step_one["consent_form_id"],
            consent_id=step_two["consent_id"],
            author_id=current_user.id,
        )

        db.session.add(spcfta)
        db.session.flush()

        for answer in step_two["checked"]:
            spcfaa = SamplePatientConsentFormAnswersAssociation(
                sample_pcf_association_id=spcfta.id,
                author_id=current_user.id,
                checked=answer,
            )

            db.session.add(spcfaa)

        spta = SampleProcessingTemplateAssociation(
            sample_id=sample.id,
            template_id=step_four["protocol_id"],
            processing_time=step_four["processing_time"],
            processing_date=step_four["processing_date"],
            author_id=current_user.id,
        )

        db.session.add(spta)
        db.session.flush()

        db.session.commit()

        clear_session(hash)

        flash("LIMBSMP: ? successfully submitted.")
        return redirect(url_for("sample.index"))

    return render_template("sample/sample/add/step_six.html", form=form, hash=hash)
'''