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
from flask import render_template, url_for, abort, session, redirect
from flask_login import login_required

from ...misc import get_internal_api_header
from ...attribute.forms import CustomAttributeSelectionForm
import requests

from uuid import uuid4

@sample.route("<uuid>/attribute/new", methods=["GET", "POST"])
@login_required
def new_custom_attribute(uuid):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    selected_attributes = []


    if sample_response.status_code == 200:

        form = CustomAttributeSelectionForm(["SAMPLE", "ALL"])


        if form.validate_on_submit():
            for fieldname, value in form.data.items():
                if value == True:
                    selected_attributes.append(int(fieldname))
            
            _hash = uuid4()
            session["custom_attr_hash_%s" % (_hash)] = selected_attributes

            return redirect(url_for("sample.new_custom_attribute_form", uuid=uuid, hash=_hash))


        return render_template(
            "sample/attribute/select.html",
            sample=sample_response.json()["content"],
            form=form,
        )


@sample.route("<uuid>/attribute/new/<hash>", methods=["GET", "POST"])
@login_required
def new_custom_attribute_form(uuid, hash):
    attribute_ids = session["custom_attr_hash_%s" % (hash)]
    
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )


    if sample_response.status_code == 200:
        form = None
        return render_template(
                "sample/attribute/form.html",
                sample=sample_response.json()["content"],
                form=form,
            )
