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


@sample.route("review/<uuid>/edit", methods=["GET", "POST"])
@login_required
def remove_review(uuid):
    return "ToDo"


@sample.route("<uuid>/associate/review", methods=["GET", "POST"])
@login_required
def associate_review(uuid):

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
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
                    "comments": form.comments.data,
                },
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
