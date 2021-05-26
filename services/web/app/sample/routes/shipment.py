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

from .. import sample
from flask_login import login_required
from flask import render_template

@sample.route("/shipment")
@login_required
def shipment_index():
    return render_template("sample/shipment/index.html")

@sample.route("/shipment/new/trolley")
@login_required
def shipment_new_step_one():
    return render_template("sample/shipment/new/step_one.html")