# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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

from ..forms import SampleReviewForm

from datetime import datetime


@sample.route("/review/<uuid>/remove", methods=["GET", "POST"])
@login_required
def remove_review(uuid: str):
    print("About to remove")
    remove_response = requests.post(
        url_for("api.sample_remove_sample_review", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )
    print("remove_response: ", remove_response.text)
    if remove_response.status_code == 200:
        flash("Review/disposal instruction Successfully Deleted!")
        sample_uuid = remove_response.json()["content"]
        return redirect(url_for("sample.view", uuid=sample_uuid))
    else:
        flash("We have a problem: %s" % (remove_response.json()))
        abort(501)


@sample.route("/review/<uuid>/edit", methods=["GET", "POST"])
@login_required
def edit_review(uuid: str):
    #form = ProtocolEventForm([])
    abort(501)


@sample.route("<uuid>/associate/review", methods=["GET", "POST"])
@login_required
def associate_review(uuid: str) -> str:

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if sample_response.status_code == 200:
        disposal_info = {}
        #disposal_id = None

        try:
            disposal_info = sample_response.json()["content"]["disposal_information"]
            print("disposal: ", disposal_info)
            if disposal_info["instruction"] in ["DES", "TRA"]:
                disposal_date = datetime.strptime(disposal_info["disposal_date"], "%Y-%m-%d").date()
                print("disposal date: ", disposal_date)
            else:
                disposal_date = None

            disposal_info = {
                "disposal_edit_on": True,
                "disposal_date": disposal_date,
                "disposal_instruction": disposal_info["instruction"],
                "disposal_comments": disposal_info["comments"],
            }

        except:
            pass

        form = SampleReviewForm(data=disposal_info)

        if form.validate_on_submit():
            review_info = {
                "review_type": form.review_type.data,
                "result": form.result.data,
                "sample_id": sample_response.json()["content"]["id"],
                "event": {
                    "undertaken_by": form.conducted_by.data,
                    "datetime": str(
                        datetime.strptime(
                            "%s %s" % (form.date.data, form.time.data),
                            "%Y-%m-%d %H:%M:%S",
                        )
                    ),
                    "comments": form.comments.data,
                },
                "quality": form.quality.data,
            }

            if form.disposal_edit_on.data:
                disposal_info = {
                        #"id": disposal_id or None,
                        #"disposal_date": disposal_date,
                        "instruction": form.disposal_instruction.data,
                        "comments": form.disposal_comments.data,
                }

                disposal_date = None
                if form.disposal_instruction.data in ["DES", "TRA"]:
                    disposal_date = str(
                        datetime.strptime(str(form.disposal_date.data), "%Y-%m-%d").date()
                    )
                    disposal_info["disposal_date"] = disposal_date

                else:
                    disposal_info["disposal_date"] = None

                print("disposal date:", disposal_date)

                review_info["disposal_info"] = disposal_info
                new_review_event_response = requests.post(
                    url_for("api.sample_new_sample_review_disposal", uuid=uuid, _external=True),
                    headers=get_internal_api_header(),
                    json=review_info
                )

                if new_review_event_response.status_code == 200:
                    flash("Sample Review and Disposal Instruction Successfully Added!")
                    return redirect(url_for("sample.view", uuid=uuid))

                else:
                    flash("Error")
            else:
                new_review_event_response = requests.post(
                    url_for("api.sample_new_sample_review_disposal", uuid=uuid, _external=True),
                    headers=get_internal_api_header(),
                    json=review_info,
                )

                if new_review_event_response.status_code == 200:
                    flash("Sample Review Successfully Added!")
                    return redirect(url_for("sample.view", uuid=uuid))

                else:
                    flash("Error")

        return render_template(
            "sample/associate/review.html",
            sample=sample_response.json()["content"],
            form=form,
        )

    abort(sample_response.status_code)
