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

from .. import sample
import requests
from flask import render_template, url_for, flash, redirect, abort
from flask_login import login_required

import requests
from ...misc import get_internal_api_header

from ..forms import (
    SampleToDocumentAssociatationForm,
    SampleReviewForm,
    ProtocolEventForm
)

from datetime import datetime


@sample.route("<uuid>", methods=["GET"])
@login_required
def view(uuid: str):
    return render_template("sample/view.html", uuid=uuid)

@sample.route("<uuid>/associate/protocol_event", methods=["GET", "POST"])
@login_required
def associate_protocol_event(uuid):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header()
    )

    if sample_response.status_code == 200:

        protocols_response = requests.get(
            url_for("api.protocol_query", _external=True),
            headers=get_internal_api_header(),
            json={"is_locked": False},
        )

        protocols = []

        if protocols_response.status_code == 200:
            for protocol in protocols_response.json()["content"]:
                protocols.append((int(protocol["id"]), "LIMBPRO-%s: %s" % (protocol["id"], protocol["name"])))

        form = ProtocolEventForm(protocols)

        if form.validate_on_submit():
            new_event = requests.post(
                url_for("api.sample_new_sample_protocol_event",_external=True),
                headers=get_internal_api_header(),
                json={
                    "datetime": str(
                            datetime.strptime(
                                "%s %s" % (form.date.data, form.time.data),
                                "%Y-%m-%d %H:%M:%S",
                            )
                    ),
                    "undertaken_by": form.undertaken_by.data,
                    "comments": form.comments.data,
                    "protocol_id": form.protocol_id.data,
                    "sample_id": sample_response.json()["content"]["id"]
                    }
            )

            if new_event.status_code == 200:
                flash("Protocol Event Successfully Added!")
                return redirect(url_for("sample.view", uuid=uuid))
            flash("We have a problem!")
        return render_template("sample/protocol/new.html", form=form, sample=sample_response.json()["content"])

@sample.route("<uuid>/associate/review", methods=["GET", "POST"])
@login_required
def associate_review(uuid):

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header()
    )

    if sample_response.status_code == 200:
        form = SampleReviewForm()


        if form.validate_on_submit():
            
            new_review_event_response = requests.post(
                url_for("api.sample_new_sample_review", uuid=uuid, _external=True),
                headers=get_internal_api_header(),
                json={
                    "review_type": form.review_type.data,
                    "result": form.result.data,
                    "sample_id": sample_response.json()["content"]["id"],
                    "conducted_by": form.conducted_by.data,
                    "datetime": str(
                            datetime.strptime(
                                "%s %s" % (form.date.data, form.time.data),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        ),
                    "quality": form.quality.data,
                    "comments": form.comments.data
                }
            )


            if new_review_event_response.status_code == 200:
                flash("Sample Review Successfully Added!")
                return redirect(url_for("sample.view", uuid=uuid))

            else:
                flash("Error")

        return render_template("sample/associate/review.html", sample=sample_response.json()["content"], form=form)
    
    abort(sample_response.status_code)

@sample.route("<uuid>/associate/document", methods=["GET", "POST"])
@login_required
def associate_document(uuid):

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if sample_response.status_code == 200:
        document_response = requests.get(
            url_for("api.document_home", _external=True),
            headers=get_internal_api_header(),
        )

        if document_response.status_code == 200:

            form = SampleToDocumentAssociatationForm(
                document_response.json()["content"]
            )

            if form.validate_on_submit():

                response = requests.post(
                    url_for("api.sample_to_document", _external=True),
                    headers=get_internal_api_header(),
                    json={
                        "sample_id": sample_response.json()["content"]["id"],
                        "document_id": form.documents.data,
                    },
                )

                if response.status_code == 200:
                    flash("Document successfully associated")
                else:
                    flash("We have a problem :( %s" % (response.json()))

                return redirect(url_for("sample.view", uuid=uuid))

            return render_template(
                "sample/associate/document.html",
                sample=sample_response.json()["content"],
                form=form,
            )

        return abort(document_response.status_code)

    return abort(sample_response.status_code)


@sample.route("<uuid>/data", methods=["GET"])
@login_required
def view_data(uuid: str):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if sample_response.status_code == 200:
        return sample_response.json()
    return sample_response.content
