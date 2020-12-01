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

from .. import sample

from ..forms import (
    CollectionConsentAndDisposalForm,
    PatientConsentQuestionnaire,
    SampleTypeSelectForm,
    ProtocolTemplateSelectForm,
    SampleReviewForm,
    CustomAttributeSelectForm,
    FinalSampleForm,
)

from datetime import datetime

import requests


def prepare_form_data(form_data: dict) -> dict:
    def _prepare_consent(consent_template_id: str, consent_data: dict):
        new_consent_data = {
            "consent_data": {
                "template_id": int(consent_template_id),
                "identifier": consent_data["consent_id"],
                "date_signed": consent_data["date_signed"],
                "comments": consent_data["comments"],
            },
            "answer_data": consent_data["checked"],
        }

        return new_consent_data

    def _prepare_processing_protocol(
        event_data: dict,
        datetime_terminology: str,
        undertaken_terminology: str,
        protocol_id: str,
    ) -> dict:
        # Can be used for both collection and processing.
        comments = None
        if comments in event_data:
            comments = event_data["comments"]
        new_processing_event = {
            "datetime": str(
                datetime.strptime(
                    "%s %s"
                    % (
                        event_data["%s_date" % (datetime_terminology)],
                        event_data["%s_time" % (datetime_terminology)],
                    ),
                    "%Y-%m-%d %H:%M:%S",
                )
            ),
            "undertaken_by": event_data["%s_by" % (undertaken_terminology)],
            "comments": comments,
            "protocol_id": protocol_id,
        }

        return new_processing_event

    def _prepare_sample_object(
        collection_data: dict,
        sample_information_data: dict,
        processing_information: dict,
        final_form_data: dict,
        sample_to_type_id: str,
        collection_event_id: str,
        processing_event_id: str,
        disposal_id: str,
        consent_id: str,
    ) -> dict:

        new_sample_data = {
            "barcode": collection_data["barcode"],
            "source": "NEW",
            "comments": final_form_data["comments"],
            "biohazard_level": sample_information_data["biohazard_level"],
            "quantity": sample_information_data["quantity"],
            "type": sample_information_data["sample_type"],
            "status": processing_information["sample_status"],
            "colour": final_form_data["colour"],
            "site_id": collection_data["site_id"],
            "sample_to_type_id": sample_to_type_id,
            "collection_event_id": collection_event_id,
            "processing_event_id": processing_event_id,
            "disposal_id": disposal_id,
            "consent_id": consent_id,
        }

        return new_sample_data

    def _prepare_disposal_object(collection_data: dict, sample_id: int) -> dict:

        if collection_data["disposal_instruction"] == "NAP":
            disposal_date = None

        else:
            disposal_date = collection_data["disposal_date"]

        new_disposal_data = {
            "instruction": collection_data["disposal_instruction"],
            "disposal_date": disposal_date,
        }

        return new_disposal_data

    def _prepare_sample_type_and_container(sample_information_data: dict) -> dict:
        sample_type_and_container_data = {}

        sample_type_and_container_data["type"] = sample_information_data["sample_type"]

        values = {}

        if sample_type_and_container_data["type"] == "FLU":
            values["fluid_container"] = sample_information_data["fluid_container"]
            values["fluid_sample_type"] = sample_information_data["fluid_sample_type"]
        elif sample_type_and_container_data["type"] == "CEL":
            values["cell_sample_type"] = sample_information_data["cell_sample_type"]
            values["tissue_sample_type"] = sample_information_data["tissue_sample_type"]
            values["fixation_type"] = sample_information_data["fixation_type"]
            values["cell_container"] = sample_information_data["cell_container"]
        elif sample_type_and_container_data["type"] == "MOL":
            values["molecular_sample_type"] = sample_information_data[
                "molecular_sample_type"
            ]
            values["fluid_container"] = sample_information_data["fluid_container"]

        sample_type_and_container_data["values"] = values

        return sample_type_and_container_data

    def _prepare_custom_attribute_data(final_form_data: dict) -> dict:
        custom_attributes = []

        for custom_attribute in final_form_data["custom_field_data"]:
            if custom_attribute[2] != "OptionField":
                custom_attributes.append(
                    {
                        "attribute_id": custom_attribute[0],
                        "option_id": custom_attribute[1],
                    }
                )
            else:
                custom_attributes.append(
                    {"attribute_id": custom_attribute[0], "data": custom_attribute[1]}
                )

        return custom_attributes

    def _prepare_sample_review_data(sample_review_data: dict) -> dict:
        sample_review_data = {
            "conducted_by": sample_review_data["conducted_by"],
            "datetime": datetime.strptime(
                "%s %s" % (sample_review_data["date"], sample_review_data["time"]),
                "%Y/%m/%d %H:%M:%S",
            ),
            "quality": sample_review_data["quality"],
            "comments": sample_review_data["comments"],
        }

        return sample_review_data

    collection_data = _prepare_processing_protocol(
        form_data["add_collection_consent_and_barcode"],
        "collection",
        "collected",
        form_data["add_collection_consent_and_barcode"]["collection_protocol_id"],
    )

    collection_response = requests.post(
        url_for("api.sample_new_sample_protocol_event", _external=True),
        headers=get_internal_api_header(),
        json=collection_data,
    )

    if collection_response.status_code != 200:
        return collection_response.content

    processing_data = _prepare_processing_protocol(
        form_data["add_processing_information"],
        "processing",
        "undertaken",
        form_data["add_processing_information"]["processing_protocol_id"],
    )

    processing_response = requests.post(
        url_for("api.sample_new_sample_protocol_event", _external=True),
        headers=get_internal_api_header(),
        json=processing_data,
    )

    if processing_response.status_code != 200:
        return processing_response.content

    consent_data = _prepare_consent(
        form_data["add_collection_consent_and_barcode"]["consent_form_id"],
        form_data["add_digital_consent_form"],
    )

    consent_response = requests.post(
        url_for("api.sample_new_sample_consent", _external=True),
        headers=get_internal_api_header(),
        json=consent_data,
    )

    if consent_response.status_code != 200:
        return consent_response.content

    type_data = _prepare_sample_type_and_container(form_data["add_sample_information"])

    type_response = requests.post(
        url_for("api.sample_new_sample_type", _external=True),
        headers=get_internal_api_header(),
        json=type_data,
    )

    if type_response.status_code != 200:
        return consent_response.content

    disposal_data = _prepare_disposal_object(
        form_data["add_collection_consent_and_barcode"], sample_id=None
    )

    disposal_response = requests.post(
        url_for("api.sample_new_disposal_instructions", _external=True),
        headers=get_internal_api_header(),
        json=disposal_data,
    )

    if disposal_response.status_code != 200:
        return disposal_response.content

    sample_data = _prepare_sample_object(
        form_data["add_collection_consent_and_barcode"],
        form_data["add_sample_information"],
        form_data["add_processing_information"],
        form_data["add_final_details"],
        type_response.json()["content"]["id"],
        collection_response.json()["content"]["id"],
        processing_response.json()["content"]["id"],
        disposal_response.json()["content"]["id"],
        consent_response.json()["content"]["id"],
    )

    sample_response = requests.post(
        url_for("api.sample_new_sample", _external=True),
        headers=get_internal_api_header(),
        json=sample_data,
    )

    # TODO: Add Review Stuff
    sample_review_data = form_data["add_sample_review"]

    return sample_response


@sample.route("add/reroute/<hash>", methods=["GET"])
@login_required
def add_rerouter(hash):
    if hash == "new":
        return redirect(url_for("sample.add_collection_consent_and_barcode"))

    query_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if query_response.status_code == 200:
        data = query_response.json()["content"]["data"]

    if "add_collection_consent_and_barcode" not in data:
        return redirect(url_for("sample.add_collection_consent_and_barcode"))
    else:
        if "add_digital_consent_form" in data:
            if "add_sample_information" in data:
                if "add_processing_information" in data:
                    if "add_sample_review" in data:
                        if "add_custom_atributes" in data:
                            if "add_final_details" in data:
                                sample_add_respose = prepare_form_data(data)
                                if sample_add_respose.status_code == 200:
                                    flash("Sample successfully added!")
                                    return redirect(
                                        sample_add_respose.json()["content"]["_links"][
                                            "self"
                                        ]
                                    )

                                else:
                                    flash(sample_add_respose.json())
                            return redirect(
                                url_for("sample.add_sample_final_form", hash=hash)
                            )
                        return redirect(
                            url_for("sample.add_custom_atributes", hash=hash)
                        )
                    return redirect(url_for("sample.add_sample_review", hash=hash))
                return redirect(url_for("sample.add_processing_information", hash=hash))
            return redirect(url_for("sample.add_sample_information", hash=hash))
        return redirect(url_for("sample.add_digital_consent_form", hash=hash))

    abort(400)


@sample.route("add/", methods=["GET", "POST"])
@login_required
def add_collection_consent_and_barcode():
    consent_templates = []
    collection_protocols = []
    processing_protocols = []
    collection_sites = []

    consent_templates_response = requests.get(
        url_for("api.consent_query", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    if consent_templates_response.status_code == 200:
        for template in consent_templates_response.json()["content"]:
            consent_templates.append(
                [template["id"], "LIMBPCF-%i: %s" % (template["id"], template["name"])]
            )

    protocols_response = requests.get(
        url_for("api.protocol_query", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    if protocols_response.status_code == 200:
        for protocol in protocols_response.json()["content"]:
            print(protocol["type"])
            if protocol["type"] == "Sample Acquisition":
                collection_protocols.append(
                    [
                        protocol["id"],
                        "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"]),
                    ]
                )
            elif protocol["type"] == "Sample Processing":
                processing_protocols.append(
                    [
                        protocol["id"],
                        "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"]),
                    ]
                )

    sites_response = requests.get(
        url_for("api.site_home", _external=True), headers=get_internal_api_header()
    )

    if sites_response.status_code == 200:
        for site in sites_response.json()["content"]:
            collection_sites.append([site["id"], site["name"]])

    form = CollectionConsentAndDisposalForm(
        consent_templates, collection_protocols, collection_sites
    )

    if form.validate_on_submit():

        route_data = {
            "barcode": form.barcode.data,
            "collection_protocol_id": form.collection_select.data,
            "collected_by": form.collected_by.data,
            "consent_form_id": form.consent_select.data,
            "site_id": form.collection_site.data,
            "collection_date": str(form.collection_date.data),
            "collection_time": str(form.collection_time.data),
            "disposal_instruction": form.disposal_instruction.data,
            "disposal_date": str(form.disposal_date.data),
            "has_donor": form.has_donor.data,
        }

        # This needs to be broken out to a new module then...
        store_response = requests.post(
            url_for("api.tmpstore_new_tmpstore", _external=True),
            headers=get_internal_api_header(),
            json={
                "data": {"add_collection_consent_and_barcode": route_data},
                "type": "SMP",
            },
        )

        if store_response.status_code == 200:

            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template(
        "sample/sample/add/step_one.html",
        form=form,
        template_count=len(consent_templates),
        collection_protocol_count=len(collection_protocols),
        processing_protocols_count=len(processing_protocols),
    )


@sample.route("add/digital_consent_form/<hash>", methods=["GET", "POST"])
@login_required
def add_digital_consent_form(hash):

    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]
    consent_id = tmpstore_data["add_collection_consent_and_barcode"]["consent_form_id"]

    consent_response = requests.get(
        url_for("api.consent_view_template", id=consent_id, _external=True),
        headers=get_internal_api_header(),
    )

    if consent_response.status_code != 200:
        abort(consent_response.status_code)

    consent_template = consent_response.json()["content"]

    questionnaire = PatientConsentQuestionnaire(consent_template)

    if questionnaire.validate_on_submit():
        consent_details = {
            "consent_id": questionnaire.consent_id.data,
            "comments": questionnaire.comments.data,
            "date_signed": str(questionnaire.date_signed.data),
            "checked": [],
        }

        for question in consent_template["questions"]:
            if getattr(questionnaire, str(question["id"])).data:
                consent_details["checked"].append(question["id"])

        tmpstore_data["add_digital_consent_form"] = consent_details

        store_response = requests.put(
            url_for("api.tmpstore_edit_tmpstore", hash=hash, _external=True),
            headers=get_internal_api_header(),
            json={"data": tmpstore_data},
        )

        if store_response.status_code == 200:
            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template(
        "sample/sample/add/step_two.html",
        hash=hash,
        consent_template=consent_template,
        questionnaire=questionnaire,
    )


@sample.route("add/sample_information/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_information(hash):
    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]

    form = SampleTypeSelectForm()

    if form.validate_on_submit():

        sample_information_details = {
            "biohazard_level": form.biohazard_level.data,
            "sample_type": form.sample_type.data,
            "fluid_sample_type": form.fluid_sample_type.data,
            "molecular_sample_type": form.molecular_sample_type.data,
            "tissue_sample_type": form.tissue_sample_type.data,
            "cell_sample_type": form.cell_sample_type.data,
            "quantity": form.quantity.data,
            "fixation_type": form.fixation_type.data,
            "fluid_container": form.fluid_container.data,
            "cell_container": form.cell_container.data,
        }

        tmpstore_data["add_sample_information"] = sample_information_details

        store_response = requests.put(
            url_for("api.tmpstore_edit_tmpstore", hash=hash, _external=True),
            headers=get_internal_api_header(),
            json={"data": tmpstore_data},
        )

        if store_response.status_code == 200:
            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template("sample/sample/add/step_three.html", form=form, hash=hash)


@sample.route("add/processing_information/<hash>", methods=["GET", "POST"])
def add_processing_information(hash):

    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]

    protocols_response = requests.get(
        url_for("api.protocol_query", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False, "type": "SAP"},
    )
    processing_protocols = []

    if protocols_response.status_code == 200:
        for protocol in protocols_response.json()["content"]:
            processing_protocols.append(
                [protocol["id"], "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"])]
            )

    form = ProtocolTemplateSelectForm(processing_protocols)

    if form.validate_on_submit():
        processing_information_details = {
            "processing_protocol_id": form.processing_protocol_id.data,
            "sample_status": form.sample_status.data,
            "processing_date": str(form.processing_date.data),
            "processing_time": form.processing_time.data.strftime("%H:%M:%S"),
            "comments": form.comments.data,
            "undertaken_by": form.undertaken_by.data,
        }

        tmpstore_data["add_processing_information"] = processing_information_details

        store_response = requests.put(
            url_for("api.tmpstore_edit_tmpstore", hash=hash, _external=True),
            headers=get_internal_api_header(),
            json={"data": tmpstore_data},
        )

        if store_response.status_code == 200:
            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template("sample/sample/add/step_four.html", form=form, hash=hash)


@sample.route("add/sample_review/<hash>", methods=["GET", "POST"])
def add_sample_review(hash):
    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]

    form = SampleReviewForm()

    if form.validate_on_submit():
        sample_review_details = {
            "quality": form.quality.data,
            "date": str(form.date.data),
            "time": form.time.data.strftime("%H:%M:%S"),
            "conducted_by": form.conducted_by.data,
            "comments": form.comments.data,
        }

        tmpstore_data["add_sample_review"] = sample_review_details

        store_response = requests.put(
            url_for("api.tmpstore_edit_tmpstore", hash=hash, _external=True),
            headers=get_internal_api_header(),
            json={"data": tmpstore_data},
        )

        if store_response.status_code == 200:
            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template("sample/sample/add/review.html", hash=hash, form=form)


@sample.route("add/custom_attributes/<hash>", methods=["GET", "POST"])
@login_required
def add_custom_atributes(hash):
    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]

    # TODO: Extend the query thing to allow for .in when passed a list

    attribute_response = requests.get(
        url_for("api.attribute_query", _external=True),
        json={},
        headers=get_internal_api_header(),
    )

    if attribute_response.status_code != 200:
        abort(attribute_response.status_code)

    form = CustomAttributeSelectForm(attribute_response.json()["content"])

    if form.validate_on_submit():

        checked = []

        for field in form:
            if field.type == "BooleanField" and field.data:
                checked.append(int(field.id))

        custom_attribute_details = {"checked": checked}

        tmpstore_data["add_custom_atributes"] = custom_attribute_details

        store_response = requests.put(
            url_for("api.tmpstore_edit_tmpstore", hash=hash, _external=True),
            headers=get_internal_api_header(),
            json={"data": tmpstore_data},
        )

        if store_response.status_code == 200:
            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template("sample/sample/add/step_five.html", form=form, hash=hash)


@sample.route("add/six/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_final_form(hash):
    # TODO: Extend the query thing to allow for .in when passed a list
    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]

    custom_attribute_ids = tmpstore_data["add_custom_atributes"]["checked"]

    custom_attributes = []
    for id in custom_attribute_ids:
        attribute_response = requests.get(
            url_for("api.attribute_view_attribute", hash=hash, id=id, _external=True),
            headers=get_internal_api_header(),
        )

        if attribute_response.status_code != 200:
            pass
        else:
            custom_attributes.append(attribute_response.json()["content"])

    form = FinalSampleForm(custom_attributes)

    if form.validate_on_submit():
        custom_field_data = []

        for field in form:
            if field.render_kw:
                custom_field_data.append([int(field.id), field.data, field.type])

        final_details = {
            "colour": form.colour.data,
            "comments": form.comments.data,
            "custom_field_data": custom_field_data,
        }

        tmpstore_data["add_final_details"] = final_details

        store_response = requests.put(
            url_for("api.tmpstore_edit_tmpstore", hash=hash, _external=True),
            headers=get_internal_api_header(),
            json={"data": tmpstore_data},
        )

        if store_response.status_code == 200:
            return redirect(
                url_for(
                    "sample.add_rerouter", hash=store_response.json()["content"]["uuid"]
                )
            )

        flash("We have a problem :( %s" % (store_response.json()))

    return render_template("sample/sample/add/step_six.html", form=form, hash=hash)
