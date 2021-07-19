# Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>
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

from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required

from ...misc import get_internal_api_header, prepare_datetime

from .. import sample

from ..forms import (
    CollectionConsentAndDisposalForm,
    PatientConsentQuestionnaire,
    FluidSampleInformationForm,
    CellSampleInformationForm,
    MolecularSampleInformationForm
)

import requests

def prepare_form_data(data: dict):

    step_one = data["step_one"]
    step_two = data["step_two"]
    step_three = data["step_three"]

    api_data = {
        "collection_information": step_one["collection_information"],
        "sample_type_information": {
        },
        "sample_information": {
            "barcode": step_one["barcode"],
            "source": "NEW",
            "base_type": step_one["sample_type"],
            "status": step_one["sample_status"],
            "site_id": step_one["site_id"],
            "biohazard_level": step_three["biohazard_level"],
            "quantity": step_three["quantity"],
        },
        "consent_information": {
            "identifier": step_two["consent_id"],
            "event": step_two["event"],
            "answers": step_two["checked"],
            "template_id": step_one["consent_form_id"],
        }
    }

    del step_three["quantity"]


    api_data["sample_type_information"] = step_three

    return api_data


@sample.route("add/reroute/<hash>", methods=["GET"])
@login_required
def add_rerouter(hash: str):

    query_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if query_response.status_code == 200 or hash != "new":
        data = query_response.json()["content"]["data"]
    else:
        return redirect(url_for("sample.add_step_one"))

    if "step_one" in data:
        if "step_two" in data:
            if "step_three" in data:
                api_data = prepare_form_data(data)

                new_sample_response = requests.post(
                    url_for("api.sample_new_sample", _external=True),
                    headers=get_internal_api_header(),
                    json=api_data,
                )

                if new_sample_response.status_code == 200:
                    return redirect(
                        new_sample_response.json()["content"]["_links"]["self"]
                    )
                else:
                    flash("We have encountered an error.")
            return redirect(url_for("sample.add_step_three", hash=hash))

        return redirect(url_for("sample.add_step_two", hash=hash))


@sample.route("add/", methods=["GET", "POST"])
@login_required
def add_step_one():
    consent_templates = []
    collection_protocols = []
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
            if protocol["type"] == "Sample Acquisition":
                collection_protocols.append(
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
            "sample_type": form.sample_type.data,
            "colour": form.colour.data,
            "sample_status": form.sample_status.data,
            "barcode": form.barcode.data,
            "collection_information" : {
                "protocol_id": form.collection_select.data,
                "event": {
                    "comments": form.collection_comments.data,
                    "undertaken_by": form.collected_by.data,
                    "datetime": prepare_datetime(
                        form.collection_date.data,
                        form.collection_time.data
                    )
                }
            },
            "consent_form_id": form.consent_select.data,
            "site_id": form.collection_site.data,
        }

        store_response = requests.post(
            url_for("api.tmpstore_new_tmpstore", _external=True),
            headers=get_internal_api_header(),
            json={
                "data": {"step_one": route_data},
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
        "sample/add/step_one.html",
        form=form,
        template_count=len(consent_templates),
        collection_protocol_count=len(collection_protocols),
    )


@sample.route("add/digital_consent_form/<hash>", methods=["GET", "POST"])
@login_required
def add_step_two(hash: str):

    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]
    consent_id = tmpstore_data["step_one"]["consent_form_id"]

    consent_response = requests.get(
        url_for("api.consent_view_template", id=consent_id, _external=True),
        headers=get_internal_api_header(),
    )

    if consent_response.status_code != 200:
        return consent_response.response

    consent_template = consent_response.json()["content"]

    questionnaire = PatientConsentQuestionnaire(consent_template)

    if questionnaire.validate_on_submit():
        consent_details = {
            "consent_id": questionnaire.consent_id.data,
            "event": {
                "datetime": prepare_datetime(
                    questionnaire.date.data,
                    questionnaire.time.data
                ),
                "comments": questionnaire.comments.data,
                "undertaken_by": questionnaire.undertaken_by.data,
            },
            "checked": [],
        }

        for question in consent_template["questions"]:
            if getattr(questionnaire, str(question["id"])).data:
                consent_details["checked"].append(question["id"])

        tmpstore_data["step_two"] = consent_details

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
        "sample/add/step_two.html",
        hash=hash,
        consent_template=consent_template,
        questionnaire=questionnaire,
    )


@sample.route("add/sample_information/<hash>", methods=["GET", "POST"])
@login_required
def add_step_three(hash: str):
    tmpstore_response = requests.get(
        url_for("api.tmpstore_view_tmpstore", hash=hash, _external=True),
        headers=get_internal_api_header(),
    )

    if tmpstore_response.status_code != 200:
        abort(tmpstore_response.status_code)

    tmpstore_data = tmpstore_response.json()["content"]["data"]

    sample_type = tmpstore_data["step_one"]["sample_type"]

    sample_information = {}
    sample_information["type"] = sample_type

    if sample_type == "FLU":

        fluid_containers_response = requests.get(
            url_for("api.container_query", _external=True),
            headers=get_internal_api_header(),
            json={"fluid": True}
        )

        if fluid_containers_response.status_code == 200:
            fluid_containers_json = fluid_containers_response.json()["content"]
            sample_information["num_containers"] = len(fluid_containers_json)
            form = FluidSampleInformationForm(fluid_containers_json)

    elif sample_type == "CEL":
        cellular_containers_response = requests.get(
            url_for("api.container_query", _external=True),
            headers=get_internal_api_header(),
            json={"cellular": True}
        )

        fixation_type_response = requests.get(
            url_for("api.container_fixation_index", _external=True),
            headers=get_internal_api_header()
        )

        if cellular_containers_response.status_code == 200 and fixation_type_response.status_code == 200:
            cellular_containers_json = cellular_containers_response.json()["content"]
            fixation_type_json = fixation_type_response.json()["content"]

            sample_information["num_containers"] = len(cellular_containers_json)
            sample_information["num_fixation"] = len(fixation_type_json)

            form = CellSampleInformationForm(cellular_containers_json, fixation_type_json)

    else:
        molecular_containers_response = requests.get(
            url_for("api.container_query", _external=True),
            headers=get_internal_api_header(),
            json={"fluid": True}
        )

        if molecular_containers_response.status_code == 200:
            molecular_containers_json = molecular_containers_response.json()["content"]
            sample_information["num_containers"] = len(molecular_containers_json)
            form = MolecularSampleInformationForm(molecular_containers_json)


    if form.validate_on_submit():
        sample_information_details = {
            "biohazard_level": form.biohazard_level.data,
            "quantity": form.quantity.data,
        }

        if sample_type == "FLU":
            sample_information_details["fluid_sample_type"] = form.fluid_sample_type.data
            sample_information_details["fluid_container_id"] = form.fluid_container.data
        elif sample_type == "CEL":
            sample_information_details["cell_sample_type"] = form.cell_sample_type.data
            sample_information_details["tissue_sample_type"] = form.tissue_sample_type.data
            sample_information_details["cell_container_id"] = form.cell_container.data
            sample_information_details["fixation_type_id"] = form.fixation_type.data
        else:
            sample_information_details["fluid_container_id"] = form.fluid_container.data
            sample_information_details["molecular_sample_type"] = form.molecular_sample_type.data

        tmpstore_data["step_three"] = sample_information_details

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

    return render_template("sample/add/step_three.html", form=form, hash=hash, sample_information=sample_information)
