# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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

import requests
from .. import sample
from flask_login import login_required
from flask import render_template, url_for
from ...misc import get_internal_api_header
from ..forms import SampleShipmentEventForm

@sample.route("/shipment/cart")
@login_required
def shipment_cart():
    return render_template("sample/shipment/cart.html")

@sample.route("/shipment/cart/data")
@login_required
def shipment_cart_data():
    cart_response = requests.get(
        url_for("api.get_cart", _external=True),
        headers=get_internal_api_header(),
    )

    return (cart_response.text, cart_response.status_code, cart_response.headers.items())


@sample.route("/shipment")
@login_required
def shipment_index():
    return render_template("sample/shipment/index.html")

@sample.route("/shipment/new/trolley")
@login_required
def shipment_new_step_one():
    sites_response = requests.get(
        url_for("api.site_home", _external=True), headers=get_internal_api_header()
    )


    if sites_response.status_code == 200:

        sites = []
        for site in sites_response.json()["content"]:
            sites.append([site["id"], "LIMBSIT-%i: %s" % (site["id"], site["name"])])


        # Get Cart
        form = SampleShipmentEventForm(sites)

        return render_template("sample/shipment/new/new.html", form=form)
    else:
        return sites_response.content